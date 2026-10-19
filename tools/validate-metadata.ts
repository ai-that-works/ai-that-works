#!/usr/bin/env bun

import { z } from 'zod';
import { readFileSync, readdirSync, statSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';
import * as yaml from 'yaml';

// Define the metadata schema
const MetadataSchema = z.object({
  guid: z.string().min(1, "GUID is required"),
  title: z.string().min(1, "Title is required"),
  description: z.string().min(1, "Description is required"),
  event_link: z.string().url("Event link must be a valid URL"),
  eventDate: z.string().datetime("Event date must be ISO 8601 format"),
  eventTime: z.string().optional(),
  event_type: z.enum(['episode', 'workshop']).optional(),
  media: z.object({
    url: z.string().url("Media URL must be valid").or(z.null()),
    type: z.enum(['video/youtube', 'audio/mpeg', 'workshop']),
  }).optional(),
  links: z.object({
    youtube: z.string().url().optional(),
    code: z.string().url().optional(),
    rsvp: z.string().url().optional(),
    discord: z.string().url().optional(),
    connect: z.string().url().optional(),
    blog: z.string().url().optional(),
  }).optional(),
  season: z.number().int().positive().or(z.string()),
  episode: z.number().int().positive().or(z.string()),
}).strict();

type EpisodeMetadata = z.infer<typeof MetadataSchema>;

interface ValidationResult {
  folder: string;
  valid: boolean;
  metadata?: EpisodeMetadata;
  errors?: string[];
  warnings?: string[];
  fixed?: boolean;
  fixedFields?: string[];
}

interface LintOptions {
  mode: 'check' | 'fix';
  repoRoot: string;
  generateReadme?: boolean;
}

function extractFrontmatter(content: string): { metadata: any; hasMetadata: boolean; contentAfterFrontmatter: string } {
  const frontmatterRegex = /^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/;
  const match = content.match(frontmatterRegex);
  
  if (!match) {
    return { metadata: null, hasMetadata: false, contentAfterFrontmatter: content };
  }

  try {
    const metadata = yaml.parse(match[1]);
    return { metadata, hasMetadata: true, contentAfterFrontmatter: match[2] };
  } catch (error) {
    throw new Error(`Failed to parse YAML frontmatter: ${error}`);
  }
}

function generateGuid(folderName: string, allFolders: string[]): string {
  // Extract episode info from folder name (YYYY-MM-DD-title)
  const match = folderName.match(/^\d{4}-\d{2}-\d{2}-(.+)$/);
  if (!match) return `aitw-${folderName}`;
  
  const title = match[1];
  if (title.includes('workshop')) {
    // For workshops, create descriptive GUIDs
    const location = title.includes('nyc') ? 'nyc' : title.includes('sf') ? 'sf' : 'workshop';
    return `aitw-workshop-${location}`;
  }
  
  // For regular episodes, generate sequential numbers based on chronological order
  const regularEpisodes = allFolders
    .filter(folder => !folder.includes('workshop'))
    .sort(); // Already sorted by date due to YYYY-MM-DD format
  
  const episodeIndex = regularEpisodes.indexOf(folderName);
  if (episodeIndex >= 0) {
    const episodeNumber = (episodeIndex + 1).toString().padStart(3, '0');
    return `aitw-${episodeNumber}`;
  }
  
  // Fallback for unknown folders
  return `aitw-${title.substring(0, 10)}`;
}

function inferMetadata(folderName: string, existingMetadata: any, repoRoot: string, allFolders: string[]): Partial<EpisodeMetadata> {
  const inferred: any = { ...existingMetadata };
  
  // Infer GUID if missing
  if (!inferred.guid) {
    inferred.guid = generateGuid(folderName, allFolders);
  }
  
  // Infer event_type if missing
  if (!inferred.event_type) {
    inferred.event_type = folderName.includes('workshop') ? 'workshop' : 'episode';
  }
  
  // Infer season if missing (default to 2)
  if (!inferred.season) {
    inferred.season = 2;
  }
  
  // Infer code link if missing
  if (!inferred.links) inferred.links = {};
  if (!inferred.links.code) {
    inferred.links.code = `${repoRoot}/tree/main/${folderName}`;
  }
  
  // Infer event_link if missing
  if (!inferred.event_link) {
    inferred.event_link = 'https://lu.ma/baml';
  }
  
  // Infer eventDate if missing (use folder date + 17:00:00Z)
  if (!inferred.eventDate) {
    const dateMatch = folderName.match(/^(\d{4}-\d{2}-\d{2})/);
    if (dateMatch) {
      inferred.eventDate = `${dateMatch[1]}T17:00:00Z`;
    }
  }
  
  return inferred;
}

function createFrontmatter(metadata: any): string {
  return '---\n' + yaml.stringify(metadata, { 
    defaultStringType: 'QUOTE_DOUBLE',
    lineWidth: 0 
  }) + '---\n\n';
}

function validateEpisodeFolder(folderPath: string, options?: LintOptions, allFolders?: string[]): ValidationResult {
  const folderName = folderPath.split('/').pop()!;
  const metaPath = join(folderPath, 'meta.md');
  const readmePath = join(folderPath, 'README.md');
  
  try {
    // Read metadata from meta.md if it exists, otherwise fall back to README.md
    let content: string;
    let isMetaFile = false;
    
    if (existsSync(metaPath)) {
      content = readFileSync(metaPath, 'utf-8');
      isMetaFile = true;
    } else if (existsSync(readmePath)) {
      content = readFileSync(readmePath, 'utf-8');
      isMetaFile = false;
    } else {
      throw new Error('Neither meta.md nor README.md found');
    }
    
    const { metadata, hasMetadata, contentAfterFrontmatter } = extractFrontmatter(content);
    
    let currentMetadata = metadata || {};
    let fixedFields: string[] = [];
    let wasFixed = false;
    
    // If no metadata or fixing mode, infer missing fields
    if (options?.mode === 'fix' || !hasMetadata) {
      const originalMetadata = { ...currentMetadata };
      const folderNames = allFolders?.map(path => path.split('/').pop()!) || [folderName];
      currentMetadata = inferMetadata(folderName, currentMetadata, options?.repoRoot || 'https://github.com/ai-that-works/ai-that-works', folderNames);
      
      // Track what was fixed
      for (const key in currentMetadata) {
        if (originalMetadata[key] !== currentMetadata[key]) {
          fixedFields.push(key);
        }
      }
      
      // If in fix mode and we have changes or no metadata at all, write the file
      if (options?.mode === 'fix' && (fixedFields.length > 0 || !hasMetadata)) {
        const newFrontmatter = createFrontmatter(currentMetadata);
        
        if (!hasMetadata || isMetaFile) {
          // Create/update meta.md for new metadata or when meta.md exists
          writeFileSync(metaPath, newFrontmatter, 'utf-8');
        } else {
          // Legacy: write to README.md with content (when README.md has frontmatter)
          const newContent = newFrontmatter + contentAfterFrontmatter;
          writeFileSync(readmePath, newContent, 'utf-8');
        }
        wasFixed = true;
      }
    }
    
    if (!hasMetadata && options?.mode !== 'fix') {
      return {
        folder: folderName,
        valid: false,
        errors: ['No YAML frontmatter found in meta.md or README.md']
      };
    }

    const result = MetadataSchema.safeParse(currentMetadata);
    const warnings: string[] = [];
    
    if (result.success) {
      // Additional validation warnings
      if (result.data.media?.url === null && result.data.media?.type !== 'workshop') {
        warnings.push('Media URL is null but type is not workshop');
      }
      
      if (!result.data.links?.youtube && result.data.media?.type === 'video/youtube') {
        warnings.push('YouTube media type but no YouTube link provided');
      }

      // Check if GUID follows expected pattern
      if (!result.data.guid.match(/^aitw-(workshop-)?[a-z0-9-]+$/)) {
        warnings.push(`GUID "${result.data.guid}" doesn't follow expected pattern (aitw-xxx or aitw-workshop-xxx)`);
      }

      return {
        folder: folderName,
        valid: true,
        metadata: result.data,
        warnings: warnings.length > 0 ? warnings : undefined,
        fixed: wasFixed,
        fixedFields: fixedFields.length > 0 ? fixedFields : undefined
      };
    } else {
      return {
        folder: folderName,
        valid: false,
        errors: result.error.errors.map(err => `${err.path.join('.')}: ${err.message}`),
        fixed: wasFixed,
        fixedFields: fixedFields.length > 0 ? fixedFields : undefined
      };
    }
  } catch (error) {
    return {
      folder: folderName,
      valid: false,
      errors: [`Error reading/parsing file: ${error}`]
    };
  }
}

function findEpisodeFolders(rootPath: string): string[] {
  const entries = readdirSync(rootPath);
  const episodeFolders: string[] = [];
  
  for (const entry of entries) {
    const fullPath = join(rootPath, entry);
    const stat = statSync(fullPath);
    
    if (stat.isDirectory() && entry.match(/^\d{4}-\d{2}-\d{2}-/)) {
      episodeFolders.push(fullPath);
    }
  }
  
  return episodeFolders.sort();
}

function parseArgs(): { mode: 'check' | 'fix'; repoRoot: string; help: boolean; generateReadme: boolean } {
  const args = process.argv.slice(2);
  let mode: 'check' | 'fix' = 'check';
  let repoRoot = 'https://github.com/ai-that-works/ai-that-works';
  let help = false;
  let generateReadme = false;
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    switch (arg) {
      case '--check':
        mode = 'check';
        break;
      case '--fix':
        mode = 'fix';
        break;
      case '--repo-root':
        repoRoot = args[++i];
        break;
      case '--generate-readme':
        generateReadme = true;
        break;
      case '--help':
      case '-h':
        help = true;
        break;
    }
  }
  
  return { mode, repoRoot, help, generateReadme };
}

function writeReadmeFile(episodes: ValidationResult[], rootPath: string): void {
  // Find the next upcoming episode
  const now = new Date();
  const upcomingEpisode = episodes
    .filter(ep => ep.valid && ep.metadata)
    .filter(ep => new Date(ep.metadata!.eventDate) > now)
    .sort((a, b) => {
      const dateA = new Date(a.metadata!.eventDate);
      const dateB = new Date(b.metadata!.eventDate);
      return dateA.getTime() - dateB.getTime();
    })[0];

  // Generate CTA section if there's an upcoming episode
  const ctaSection = upcomingEpisode ? `

<div align="center">
<h2>🦄 <strong>Next Episode</strong></h2>
<h3><strong>${upcomingEpisode.metadata!.title.replace(/🦄\s*ai that works:\s*/i, '')}</strong></h3>
<p><strong>${new Date(upcomingEpisode.metadata!.eventDate).toLocaleDateString('en-US', { 
  weekday: 'long', 
  year: 'numeric', 
  month: 'long', 
  day: 'numeric' 
})} at ${upcomingEpisode.metadata!.eventTime ?? '10 AM PST'}</strong></p>
<p><em>${upcomingEpisode.metadata!.description}</em></p>

<a href="${upcomingEpisode.metadata!.event_link}" target="_blank">
<img src="https://img.shields.io/badge/🦄_REGISTER_NOW-Join_Live_Session-ff4444?style=for-the-badge&logo=calendar" alt="Register Now">
</a>

</div>

---
` : '';

  // Fixed header content with clean, modern design
  const fixedContent = `<div align="center">

# 🦄 **AI That Works**

*On Zoom, Tuesdays at 10 AM PST - an hour of live coding, Q&A, and production-ready AI engineering*

[![Event Calendar](https://img.shields.io/badge/Events-lu.ma%2Fbaml-2ea44f?style=for-the-badge&logo=calendar)](https://lu.ma/baml)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865f2?style=for-the-badge&logo=discord&logoColor=white)](https://boundaryml.com/discord)
[![YouTube Playlist](https://img.shields.io/badge/YouTube-Watch%20All%20Episodes-ff0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/playlist?list=PLi60mUelRAbFqfgymVfZttlkIyt0XHZjt)

</div>${ctaSection}

---

## **What We're About**

> **Weekly conversations** with [@hellovai](https://www.github.com/hellovai) & [@dexhorthy](https://www.github.com/dexhorthy) about getting the **most juice** out of today's models

**When:** Every Tuesday at **10 AM PST** on Zoom  
**Duration:** 1 hour of live coding, Q&A, and production-ready insights  
**Goal:** Take your AI app from **demo → production**

<div align="center">
<strong>Let's code together.</strong>
</div>

---

## **Pre-Reading & Setup**

Before joining, get familiar with our toolkit:

<table>
<tr>
<td width="33%">

### **Core Tools**
- **Zoom** - Live sessions
- **Cursor** - AI-powered IDE  
- **Git** - Version control
- **Claude Code** - Agentic Coding
- **CodeLayer** - Agentic Coding Tool

</td>
<td width="33%">

### **Languages**
- **Python/TypeScript/Go** - Application logic
- **BAML** - Prompting DSL
  - [Repository](https://github.com/boundaryml/baml)
  - [Getting Started Guide](https://gloochat.notion.site/benefits-of-baml)

</td>
<td width="33%">

### **Package Managers**
- **Python:** [UV](https://docs.astral.sh/uv/getting-started/installation)
- **TypeScript:** PNPM
- **Go:** Go modules

</td>
</tr>
</table>

---

## **Episodes & Workshops**

<div align="center">
<em>From Demo to Production - One Episode at a Time</em>
</div>

<br>

<table>
<thead>
<tr>
<th align="left" width="40%">📅 <strong>Episode</strong></th>
<th align="left" width="60%">📝 <strong>Description</strong></th>
</tr>
</thead>
<tbody>`;

  // Filter and sort episodes
  const validEpisodes = episodes
    .filter(ep => ep.valid && ep.metadata)
    .sort((a, b) => {
      // Sort by eventDate descending (newest first)
      const dateA = new Date(a.metadata!.eventDate);
      const dateB = new Date(b.metadata!.eventDate);
      return dateB.getTime() - dateA.getTime();
    });

  // Filter out workshops and sort episodes chronologically for numbering
  const episodesOnly = validEpisodes.filter(ep => 
    !ep.metadata?.title.toLowerCase().includes('workshop') && 
    ep.metadata?.event_type !== 'workshop'
  ).sort((a, b) => {
    // Sort by eventDate ascending (oldest first) for sequential numbering
    const dateA = new Date(a.metadata!.eventDate);
    const dateB = new Date(b.metadata!.eventDate);
    return dateA.getTime() - dateB.getTime();
  });

  // Create episode number mapping
  const episodeNumberMap = new Map<string, number>();
  episodesOnly.forEach((ep, index) => {
    const folderName = ep.folder.split('/').pop()!;
    episodeNumberMap.set(folderName, index + 1);
  });

  // Generate table rows
  const tableRows = validEpisodes.map(ep => {
    const metadata = ep.metadata!;
    const eventDate = new Date(metadata.eventDate);
    const dateStr = eventDate.toISOString().split('T')[0];
    
    // Extract episode number and title
    const cleanTitle = metadata.title.replace(/🦄\s*ai that works:\s*/i, '').replace(/^S\d+E\d+\s*[–-]\s*/, '');
    const folderName = ep.folder.split('/').pop()!;
    const isWorkshop = metadata.title.toLowerCase().includes('workshop') || metadata.event_type === 'workshop';
    const episodeNum = isWorkshop ? 
      (metadata.title.includes('NYC') ? 'NYC Workshop' : 
       metadata.title.includes('SF') ? 'SF Workshop' : 'Workshop') : 
      episodeNumberMap.get(folderName)?.toString() || metadata.episode.toString();
    
    // Determine if this is past or future
    const now = new Date();
    const isPast = eventDate < now;
    
    // Build links section
    const links = [];
    if (isPast && metadata.links?.youtube) {
      links.push(`[youtube](${metadata.links.youtube})`);
    }
    if (metadata.links?.code) {
      const codeUrl = metadata.links.code
        .replace('https://github.com/ai-that-works/ai-that-works/tree/main/', './')
      links.push(`[code](${codeUrl})`);
    }
    if (!isPast) {
      links.push(`[RSVP](${metadata.event_link})`);
    }
    if (isPast) {
      links.push('PAST');
    }
    
    const linksStr = links.join(' • ');
    
    // Format the row with enhanced styling
    const episodeTitle = isWorkshop ? 
      `<strong>${episodeNum}</strong>: ${cleanTitle}` : 
      `<strong>#${episodeNum}</strong>: ${cleanTitle}`;
    
    const statusBadge = isPast ? 
      '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold;">PAST</span>' :
      '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold;">UPCOMING</span>';
    
    const linksList = links.filter(link => !link.includes('PAST')).map(link => {
      if (link.includes('youtube')) {
        const url = link.match(/\(([^)]+)\)/)?.[1] || '#';
        return `<a href="${url}">watch</a>`;
      } else if (link.includes('code')) {
        const url = link.match(/\(([^)]+)\)/)?.[1] || '#';
        return `<a href="${url}">code</a>`;
      } else if (link.includes('RSVP')) {
        const url = link.match(/\(([^)]+)\)/)?.[1] || '#';
        return `<a href="${url}">register</a>`;
      }
      return link;
    }).join(' • ');
    
    const topicCell = `
      <div style="padding: 8px 0;">
        <div style="margin-bottom: 2px;">
          ${statusBadge}
        </div>
        <div style="color: #666; font-size: 13px; margin-bottom: 4px;">${dateStr}</div>
        <div style="font-size: 16px; line-height: 1.3; margin-bottom: 6px;">${episodeTitle}</div>
        <div style="font-size: 13px; color: #666;">
          ${linksList}
        </div>
      </div>
    `;
    
    const descriptionCell = `<div style="padding: 8px 0; line-height: 1.5;">${metadata.description}</div>`;
    
    return `<tr><td>${topicCell}</td><td>${descriptionCell}</td></tr>`;
  }).join('\n');

  // Combine everything
  const fullContent = `${fixedContent}\n${tableRows}\n</tbody>\n</table>\n`;
  
  // Write to README.md
  const readmePath = join(rootPath, 'README.md');
  writeFileSync(readmePath, fullContent, 'utf-8');
  console.log(`📝 Generated ${readmePath}`);
}

function showHelp() {
  console.log(`
🦄 AI That Works - Episode Metadata Validator & Linter

Usage: bun run validate-metadata.ts [options]

Options:
  --check            Validate metadata only (default)
  --fix              Auto-fix missing metadata fields
  --generate-readme  Generate root README.md with automated episode table + RSS feed + data.json
  --repo-root        Repository root URL (default: https://github.com/ai-that-works/ai-that-works)
  --help, -h         Show this help message

Examples:
  bun run validate-metadata.ts --check
  bun run validate-metadata.ts --fix
  bun run validate-metadata.ts --generate-readme
  bun run validate-metadata.ts --fix --generate-readme
  bun run validate-metadata.ts --fix --repo-root https://github.com/custom/repo

Auto-fixes:
  • Missing GUID (generated from folder name)
  • Missing event_type (episode/workshop based on folder name)
  • Missing season (defaults to 2)
  • Missing code link (inferred from folder path)
  • Missing event_link (defaults to https://lu.ma/baml)
  • Missing eventDate (inferred from folder date)
`);
}

function main() {
  const { mode, repoRoot, help, generateReadme } = parseArgs();
  
  if (help) {
    showHelp();
    return;
  }
  
  // Always run from the repo root, regardless of where the script is called from
  const cwd = process.cwd();
  const rootPath = cwd.endsWith('/tools') ? join(cwd, '..') : cwd;
  
  const modeEmoji = mode === 'fix' ? '🔧' : '🔍';
  const modeText = mode === 'fix' ? 'Linting and fixing' : 'Validating';
  console.log(`${modeEmoji} ${modeText} episode metadata in: ${rootPath}\n`);
  
  const options: LintOptions = { mode, repoRoot, generateReadme };
  const episodeFolders = findEpisodeFolders(rootPath);
  const results: ValidationResult[] = [];
  
  for (const folder of episodeFolders) {
    const result = validateEpisodeFolder(folder, options, episodeFolders);
    results.push(result);
  }
  
  // Generate README.md, RSS feed, and data.json if requested
  if (options.generateReadme) {
    writeReadmeFile(results, rootPath);
    generateRSSFeed(results, rootPath);
    generateDataJson(results, rootPath);
  }

  // Print results
  let validCount = 0;
  let totalCount = results.length;
  let fixedCount = 0;
  
  for (const result of results) {
    if (result.fixed) fixedCount++;
    
    if (result.valid) {
      validCount++;
      const fixedText = result.fixed ? ' 🔧' : '';
      console.log(`✅ ${result.folder}${fixedText}`);
      
      if (result.fixedFields) {
        console.log(`   🔧 Fixed: ${result.fixedFields.join(', ')}`);
      }
      
      if (result.warnings) {
        for (const warning of result.warnings) {
          console.log(`   ⚠️  ${warning}`);
        }
      }
    } else {
      const fixedText = result.fixed ? ' 🔧' : '';
      console.log(`❌ ${result.folder}${fixedText}`);
      
      if (result.fixedFields) {
        console.log(`   🔧 Fixed: ${result.fixedFields.join(', ')}`);
      }
      
      if (result.errors) {
        for (const error of result.errors) {
          console.log(`   🚨 ${error}`);
        }
      }
    }
  }
  
  const fixSummary = mode === 'fix' && fixedCount > 0 ? ` (${fixedCount} fixed)` : '';
  console.log(`\n📊 Summary: ${validCount}/${totalCount} episodes have valid metadata${fixSummary}`);
  
  // Print statistics
  const guidCounts = new Map<string, number>();
  const seasonCounts = new Map<string, number>();
  
  for (const result of results) {
    if (result.valid && result.metadata) {
      // Count GUIDs to check for duplicates
      const guid = result.metadata.guid;
      guidCounts.set(guid, (guidCounts.get(guid) || 0) + 1);
      
      // Count seasons
      const season = result.metadata.season.toString();
      seasonCounts.set(season, (seasonCounts.get(season) || 0) + 1);
    }
  }
  
  // Check for duplicate GUIDs
  const duplicateGuids = Array.from(guidCounts.entries()).filter(([_, count]) => count > 1);
  if (duplicateGuids.length > 0) {
    console.log(`\n🚨 Duplicate GUIDs found:`);
    for (const [guid, count] of duplicateGuids) {
      console.log(`   ${guid}: ${count} occurrences`);
    }
  }
  
  // Show season distribution
  console.log(`\n📈 Season distribution:`);
  for (const [season, count] of Array.from(seasonCounts.entries()).sort()) {
    console.log(`   Season ${season}: ${count} episodes`);
  }
  
  // Exit with error code if validation failed
  if (validCount < totalCount) {
    process.exit(1);
  }
}

if (import.meta.main) {
  main();
}

function escapeXml(unsafe: string): string {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;")
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, ""); // Remove control characters
}

function generateRSSFeed(episodes: ValidationResult[], rootPath: string): void {
  // Filter to completed episodes with YouTube links
  const completedEpisodes = episodes
    .filter(ep => ep.valid && ep.metadata)
    .filter(ep => {
      const eventDate = new Date(ep.metadata!.eventDate);
      const now = new Date();
      return eventDate < now && ep.metadata!.links?.youtube;
    })
    .sort((a, b) => {
      // Sort by date descending (newest first) for RSS
      const dateA = new Date(a.metadata!.eventDate);
      const dateB = new Date(b.metadata!.eventDate);
      return dateB.getTime() - dateA.getTime();
    });

  const rssItems = completedEpisodes.map(ep => {
    const metadata = ep.metadata!;
    const pubDate = new Date(metadata.eventDate).toUTCString();
    const cleanTitle = metadata.title.replace(/🦄\s*ai that works:\s*/i, '');
    const folderName = ep.folder.split('/').pop()!;
    const isWorkshop = metadata.title.toLowerCase().includes('workshop') || metadata.event_type === 'workshop';
    const episodeNum = isWorkshop ? 
      (metadata.title.includes('NYC') ? 'NYC Workshop' : 
       metadata.title.includes('SF') ? 'SF Workshop' : 'Workshop') : 
      metadata.episode.toString();
    
    const guid = metadata.guid || `aitw-${folderName}`;
    const youtubeUrl = metadata.links!.youtube!;
    const codeUrl = metadata.links?.code || `https://github.com/ai-that-works/ai-that-works/tree/main/${folderName}`;
    
    const description = `${metadata.description}

Watch: ${youtubeUrl}
Code: ${codeUrl}
Event: ${metadata.event_link}

AI That Works - Weekly conversations about production-ready AI engineering with live coding and Q&A.`;

    return `    <item>
      <title><![CDATA[${cleanTitle}]]></title>
      <description><![CDATA[${description}]]></description>
      <link>${escapeXml(youtubeUrl)}</link>
      <guid isPermaLink="false">${escapeXml(guid)}</guid>
      <pubDate>${pubDate}</pubDate>
      <category>Technology</category>
      <category>Software Engineering</category>
      <category>Artificial Intelligence</category>
      <enclosure url="${escapeXml(youtubeUrl)}" type="video/youtube" />
    </item>`;
  }).join('\n');

  const rssContent = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title><![CDATA[🦄 AI That Works]]></title>
    <description><![CDATA[Weekly conversations about production-ready AI engineering. Live coding, Q&A, and deep dives into real-world AI systems. Every Tuesday at 10 AM PST on Zoom.]]></description>
    <link>https://github.com/ai-that-works/ai-that-works</link>
    <language>en-us</language>
    <managingEditor>hello@boundaryml.com (AI That Works)</managingEditor>
    <webMaster>hello@boundaryml.com (AI That Works)</webMaster>
    <category>Technology</category>
    <category>Software Engineering</category>
    <category>Artificial Intelligence</category>
    <image>
      <url>https://github.com/ai-that-works/ai-that-works/raw/main/assets/logo.png</url>
      <title><![CDATA[🦄 AI That Works]]></title>
      <link>https://github.com/ai-that-works/ai-that-works</link>
    </image>
    <atom:link href="https://github.com/ai-that-works/ai-that-works/raw/main/feed.xml" rel="self" type="application/rss+xml" />
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <ttl>1440</ttl>
${rssItems}
  </channel>
</rss>`;

  // Write RSS feed
  const rssPath = join(rootPath, 'feed.xml');
  writeFileSync(rssPath, rssContent, 'utf-8');
  console.log(`📡 Generated RSS feed: ${rssPath} (${completedEpisodes.length} episodes)`);
}

function generateDataJson(episodes: ValidationResult[], rootPath: string): void {
  // Filter to valid episodes and extract metadata
  const episodeData = episodes
    .filter(ep => ep.valid && ep.metadata)
    .map(ep => {
      const metadata = ep.metadata!;
      const folderName = ep.folder.split('/').pop()!;
      
      return {
        folder: folderName,
        ...metadata,
        // Ensure consistent data types
        season: Number(metadata.season),
        episode: Number(metadata.episode),
        eventDate: metadata.eventDate,
        // Add computed fields
        isPast: new Date(metadata.eventDate) < new Date(),
        isWorkshop: metadata.title.toLowerCase().includes('workshop') || metadata.event_type === 'workshop'
      };
    })
    .sort((a, b) => {
      // Sort by eventDate descending (newest first)
      const dateA = new Date(a.eventDate);
      const dateB = new Date(b.eventDate);
      return dateB.getTime() - dateA.getTime();
    });

  const dataJson = {
    episodes: episodeData,
    meta: {
      totalEpisodes: episodeData.length,
      completedEpisodes: episodeData.filter(ep => ep.isPast && ep.links?.youtube).length,
      upcomingEpisodes: episodeData.filter(ep => !ep.isPast).length,
      workshops: episodeData.filter(ep => ep.isWorkshop).length,
      seasons: Array.from(new Set(episodeData.map(ep => ep.season))).sort(),
      lastUpdated: new Date().toISOString(),
      generatedBy: 'validate-metadata.ts'
    }
  };

  // Write data.json
  const dataPath = join(rootPath, 'data.json');
  writeFileSync(dataPath, JSON.stringify(dataJson, null, 2), 'utf-8');
  console.log(`📄 Generated data.json: ${dataPath} (${episodeData.length} episodes)`);
}

export { MetadataSchema, validateEpisodeFolder, generateGuid, writeReadmeFile, generateRSSFeed, generateDataJson, type EpisodeMetadata };
