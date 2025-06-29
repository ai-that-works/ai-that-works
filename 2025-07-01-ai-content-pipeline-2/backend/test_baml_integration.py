#!/usr/bin/env python3
"""
Test script to verify BAML integration works correctly
"""
import os
from dotenv import load_dotenv
from baml_client import b, types

def test_baml_summarize():
    """Test the BAML SummarizeVideo function"""
    load_dotenv()
    
    # Check if API keys are available
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        print("❌ ERROR: No AI API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file")
        return False
    
    # Test transcript
    test_transcript = """
    Welcome everyone to today's meeting about our AI content pipeline project. 
    
    First, let me give you an overview of what we've accomplished. We've successfully 
    integrated Zoom recording processing with automatic transcript generation. The system 
    can now download recordings, extract audio, and generate accurate transcripts.
    
    Our key achievements include:
    - Automated video download from Zoom API
    - High-quality transcript generation using Whisper
    - Database integration for storing video metadata
    - RESTful API for frontend interaction
    
    Looking ahead, we need to focus on three main areas:
    1. Content generation using AI models
    2. Multi-platform content adaptation 
    3. User feedback integration for continuous improvement
    
    The next steps are to implement AI-powered summarization and draft generation 
    for different social media platforms.
    """
    
    try:
        print("🚀 Testing BAML SummarizeVideo function...")
        
        # Call BAML SummarizeVideo function
        summary: types.VideoSummary = b.SummarizeVideo(
            transcript=test_transcript,
            title="AI Content Pipeline Project Update"
        )
        
        print("✅ BAML SummarizeVideo executed successfully!")
        print(f"📝 Bullet Points ({len(summary.bullet_points)}):")
        for i, point in enumerate(summary.bullet_points, 1):
            print(f"   {i}. {point}")
        
        print(f"\n🎯 Key Topics ({len(summary.key_topics)}):")
        for i, topic in enumerate(summary.key_topics, 1):
            print(f"   {i}. {topic}")
        
        print(f"\n💡 Main Takeaways ({len(summary.main_takeaways)}):")
        for i, takeaway in enumerate(summary.main_takeaways, 1):
            print(f"   {i}. {takeaway}")
        
        # Test content generation functions
        print("\n🚀 Testing social media content generation...")
        
        # Generate email draft
        email: types.EmailDraft = b.GenerateEmailDraft(
            summary=summary,
            video_title="AI Content Pipeline Project Update"
        )
        print(f"\n📧 Email Draft:")
        print(f"   Subject: {email.subject}")
        print(f"   Body: {email.body[:100]}...")
        print(f"   CTA: {email.call_to_action}")
        
        # Generate Twitter thread
        twitter: types.TwitterThread = b.GenerateTwitterThread(
            summary=summary,
            video_title="AI Content Pipeline Project Update"
        )
        print(f"\n🐦 Twitter Thread ({len(twitter.tweets)} tweets):")
        for i, tweet in enumerate(twitter.tweets, 1):
            print(f"   {i}/{len(twitter.tweets)}: {tweet[:80]}...")
        print(f"   Hashtags: {', '.join(twitter.hashtags)}")
        
        # Generate LinkedIn post
        linkedin: types.LinkedInPost = b.GenerateLinkedInPost(
            summary=summary,
            video_title="AI Content Pipeline Project Update"
        )
        print(f"\n💼 LinkedIn Post:")
        print(f"   Content: {linkedin.content[:100]}...")
        print(f"   Hashtags: {', '.join(linkedin.hashtags)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: BAML function failed: {e}")
        return False

if __name__ == "__main__":
    success = test_baml_summarize()
    if success:
        print("\n🎉 BAML integration test passed! Your summarize endpoint should work correctly.")
    else:
        print("\n💥 BAML integration test failed. Please check your API keys and BAML configuration.")