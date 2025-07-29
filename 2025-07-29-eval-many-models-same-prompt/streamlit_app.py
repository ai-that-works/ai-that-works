import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd
import re

def detect_llm_patterns(text):
    """Detect LLM-characteristic patterns in text"""
    if not isinstance(text, str):
        return []
    
    patterns = []
    
    # Em-dashes and en-dashes
    em_dash_matches = re.finditer(r'[—–]', text)
    for match in em_dash_matches:
        patterns.append({
            'type': 'em_dash',
            'start': match.start(),
            'end': match.end(),
            'text': match.group(),
            'description': 'Em-dash (common in LLM text)'
        })
    
    # Hyperbolic/superlative language
    hyperbolic_words = [
        r'\bundoubtedly\b', r'\bcertainly\b', r'\bdefinitely\b', r'\babsolutely\b',
        r'\bincredibly\b', r'\bextraordinarily\b', r'\bremarkably\b', r'\bunquestionably\b',
        r'\bphenomenal\b', r'\bexceptional\b', r'\boutstanding\b', r'\bunparalleled\b',
        r'\bgroundbreaking\b', r'\brevolutionary\b', r'\btransformative\b', r'\bcomprehensive\b',
        r'\bseamlessly\b', r'\beffortlessly\b', r'\bcrucial\b', r'\bvital\b', r'\bessential\b',
        r'\bfundamental\b', r'\binvaluable\b', r'\bindispensable\b'
    ]
    
    for pattern in hyperbolic_words:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            patterns.append({
                'type': 'hyperbolic',
                'start': match.start(),
                'end': match.end(),
                'text': match.group(),
                'description': 'Hyperbolic/superlative language'
            })
    
    # Lists with consistent formatting (bullet points)
    bullet_patterns = re.finditer(r'^[•·▪▫■□‣⁃]\s', text, re.MULTILINE)
    for match in bullet_patterns:
        patterns.append({
            'type': 'bullet_point',
            'start': match.start(),
            'end': match.end(),
            'text': match.group(),
            'description': 'Formatted bullet point'
        })
    
    # Formal transitions
    formal_transitions = [
        r'\bfurthermore\b', r'\bmooreover\b', r'\badditionally\b', r'\bconsequently\b',
        r'\btherefore\b', r'\bhowever\b', r'\bnevertheless\b', r'\bnonetheless\b',
        r'\bin conclusion\b', r'\bin summary\b', r'\bto summarize\b', r'\bultimately\b',
        r'\bin essence\b', r'\bat its core\b', r'\bfundamentally\b'
    ]
    
    for pattern in formal_transitions:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            patterns.append({
                'type': 'formal_transition',
                'start': match.start(),
                'end': match.end(),
                'text': match.group(),
                'description': 'Formal transition phrase'
            })
    
    # Hedging language
    hedging_patterns = [
        r'\bpotentially\b', r'\bpossibly\b', r'\blikely\b', r'\bmay\b', r'\bmight\b',
        r'\bcould\b', r'\bwould\b', r'\bshould\b', r'\btend to\b', r'\boften\b',
        r'\btypically\b', r'\bgenerally\b', r'\busually\b', r'\bfrequently\b'
    ]
    
    for pattern in hedging_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            patterns.append({
                'type': 'hedging',
                'start': match.start(),
                'end': match.end(),
                'text': match.group(),
                'description': 'Hedging language'
            })
    
    # Overuse of quotation marks for emphasis
    quote_emphasis = re.finditer(r'"[^"]*"', text)
    for match in quote_emphasis:
        if len(match.group()) > 2:  # More than just empty quotes
            patterns.append({
                'type': 'quote_emphasis',
                'start': match.start(),
                'end': match.end(),
                'text': match.group(),
                'description': 'Quotation marks for emphasis'
            })
    
    return sorted(patterns, key=lambda x: x['start'])

def highlight_text_with_patterns(text, patterns, highlight_enabled=True):
    """Apply HTML highlighting to text based on detected patterns"""
    if not highlight_enabled or not patterns:
        return text
    
    # Color scheme for different pattern types (dark mode friendly)
    colors = {
        'em_dash': '#8B2635',       # Dark red
        'hyperbolic': '#8B7500',    # Dark yellow/gold
        'bullet_point': '#2D5A2D',  # Dark green
        'formal_transition': '#2D2D8B',  # Dark blue
        'hedging': '#6B2D6B',       # Dark magenta
        'quote_emphasis': '#8B4513'  # Dark orange/brown
    }
    
    # Sort patterns by start position in reverse order to avoid offset issues
    sorted_patterns = sorted(patterns, key=lambda x: x['start'], reverse=True)
    
    result = text
    for pattern in sorted_patterns:
        color = colors.get(pattern['type'], '#f0f0f0')
        highlighted = f'<span style="background-color: {color}; padding: 1px 2px; border-radius: 2px;" title="{pattern["description"]}">{pattern["text"]}</span>'
        result = result[:pattern['start']] + highlighted + result[pattern['end']:]
    
    return result

def display_text_with_llm_detection(text, highlight_enabled=True, label=""):
    """Display text with optional LLM pattern highlighting and statistics"""
    if not isinstance(text, str):
        st.write(text)
        return
    
    patterns = detect_llm_patterns(text)
    
    if highlight_enabled and patterns:
        # Show pattern statistics
        pattern_counts = {}
        for pattern in patterns:
            pattern_type = pattern['type'].replace('_', ' ').title()
            pattern_counts[pattern_type] = pattern_counts.get(pattern_type, 0) + 1
        
        if pattern_counts:
            st.caption(f"🤖 LLM patterns detected: {', '.join([f'{k}: {v}' for k, v in pattern_counts.items()])}")
        
        # Display highlighted text
        highlighted_text = highlight_text_with_patterns(text, patterns, highlight_enabled)
        st.markdown(highlighted_text, unsafe_allow_html=True)
    else:
        st.write(text)

def load_results():
    """Load all results from the results directory with structure {test}/{model}.json"""
    results_dir = Path("results")
    results = {}
    
    if not results_dir.exists():
        return results
    
    # Look for test directories
    for test_dir in results_dir.iterdir():
        if test_dir.is_dir():
            test_name = test_dir.name
            
            # Look for model JSON files in each test directory
            for file_path in test_dir.glob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Model name is the filename without extension
                    model = file_path.stem
                    
                    result_key = f"{test_name}_{model}"
                    results[result_key] = {
                        'test_name': test_name,
                        'model': model,
                        'data': data,
                        'file_path': str(file_path)
                    }
                except Exception as e:
                    st.error(f"Error loading {file_path}: {str(e)}")
    
    return results

def main():
    st.set_page_config(page_title="AI Model Results Viewer", layout="wide")
    
    st.title("AI Model Results Viewer")
    st.write("View and compare results from the results directory")
    
    # Load results
    results = load_results()
    
    if not results:
        st.warning("No results found in the results directory. Run your evaluation first to generate results.")
        return
    
    # Sidebar for filtering
    with st.sidebar:
        st.header("Filters")
        
        # Get unique test names and models
        test_names = sorted(set(r['test_name'] for r in results.values()))
        models = sorted(set(r['model'] for r in results.values()))
        
        selected_tests = st.multiselect(
            "Select Tests",
            test_names,
            default=test_names
        )
        
        selected_models = st.multiselect(
            "Select Models", 
            models,
            default=models
        )
        
        # Display options
        st.header("Display Options")
        show_raw_json = st.checkbox("Show Raw JSON", value=False)
        comparison_mode = st.checkbox("Comparison Mode", value=True)
        highlight_llm = st.checkbox("Highlight LLM Patterns", value=True, help="Highlight em-dashes, hyperbolic language, and other LLM-characteristic patterns")
        
        if highlight_llm:
            with st.expander("LLM Pattern Legend"):
                st.markdown("""
                <div style="font-size: 0.8em;">
                <span style="background-color: #8B2635; color: white; padding: 2px 6px; border-radius: 3px;">Em-dashes</span> - Common in LLM text<br><br>
                <span style="background-color: #8B7500; color: white; padding: 2px 6px; border-radius: 3px;">Hyperbolic</span> - Superlative language<br><br>
                <span style="background-color: #2D5A2D; color: white; padding: 2px 6px; border-radius: 3px;">Bullet points</span> - Formatted lists<br><br>
                <span style="background-color: #2D2D8B; color: white; padding: 2px 6px; border-radius: 3px;">Formal transitions</span> - "Furthermore", "however", etc.<br><br>
                <span style="background-color: #6B2D6B; color: white; padding: 2px 6px; border-radius: 3px;">Hedging</span> - "Possibly", "might", "could", etc.<br><br>
                <span style="background-color: #8B4513; color: white; padding: 2px 6px; border-radius: 3px;">Quote emphasis</span> - Quotation marks for emphasis
                </div>
                """, unsafe_allow_html=True)
    
    # Filter results
    filtered_results = {
        k: v for k, v in results.items() 
        if v['test_name'] in selected_tests and v['model'] in selected_models
    }
    
    if not filtered_results:
        st.warning("No results match the selected filters.")
        return
    
    # Display summary
    st.header("Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Results", len(filtered_results))
    with col2:
        st.metric("Tests", len(set(r['test_name'] for r in filtered_results.values())))
    with col3:
        st.metric("Models", len(set(r['model'] for r in filtered_results.values())))
    
    # Display results
    if comparison_mode:
        st.header("Model Comparison")
        
        # For each selected test, show side-by-side comparison
        for test_name in selected_tests:
            test_results = {k: v for k, v in filtered_results.items() if v['test_name'] == test_name}
            if not test_results:
                continue
                
            st.subheader(f"Test: {test_name}")
            
            # Get available models for this test
            available_models = [v['model'] for v in test_results.values()]
            
            if len(available_models) < 2:
                st.warning(f"Need at least 2 models for comparison. Found: {len(available_models)}")
                continue
            
            # Create dropdowns for model selection
            col1, col2 = st.columns(2)
            
            with col1:
                model_1 = st.selectbox(
                    "Select first model", 
                    available_models,
                    key=f"model1_{test_name}",
                    index=0
                )
            
            with col2:
                model_2 = st.selectbox(
                    "Select second model", 
                    available_models,
                    key=f"model2_{test_name}",
                    index=1 if len(available_models) > 1 else 0
                )
            
            # Display comparison
            comp_col1, comp_col2 = st.columns(2)
            
            for col, model in [(comp_col1, model_1), (comp_col2, model_2)]:
                model_result = next((v for v in test_results.values() if v['model'] == model), None)
                
                with col:
                    st.write(f"**{model}**")
                    
                    if model_result:
                        data = model_result['data']
                        
                        # Display key fields
                        if isinstance(data, dict):
                            if 'subject' in data:
                                st.write("**Subject:**")
                                display_text_with_llm_detection(data['subject'], highlight_llm)
                            
                            if 'body' in data:
                                st.write("**Body:**")
                                with st.expander("View Body", expanded=False):
                                    display_text_with_llm_detection(data['body'], highlight_llm)
                            
                            if 'we_covered' in data:
                                st.write("**We Covered:**")
                                display_text_with_llm_detection(data['we_covered'], highlight_llm)
                            
                            if 'quick_recap' in data:
                                st.write("**Quick Recap:**")
                                for item in data['quick_recap']:
                                    display_text_with_llm_detection(f"• {item}", highlight_llm)
                            
                            if 'one_thing_to_remember' in data:
                                st.write("**One Thing to Remember:**")
                                display_text_with_llm_detection(data['one_thing_to_remember'], highlight_llm)
                            
                            if 'next_session' in data:
                                st.write("**Next Session:**")
                                display_text_with_llm_detection(data['next_session'], highlight_llm)
                        
                        if show_raw_json:
                            with st.expander("Raw JSON"):
                                st.json(data)
                    else:
                        st.write("*No result available*")
            
            st.divider()
    
    else:
        st.header("All Results")
        
        # Display each result individually
        for filename, result in filtered_results.items():
            with st.expander(f"{result['model']} - {result['test_name']}", expanded=False):
                data = result['data']
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if isinstance(data, dict):
                        # Display structured data
                        for key, value in data.items():
                            st.write(f"**{key.replace('_', ' ').title()}:**")
                            if isinstance(value, list):
                                for item in value:
                                    display_text_with_llm_detection(f"• {item}", highlight_llm)
                            else:
                                display_text_with_llm_detection(str(value), highlight_llm)
                            st.write("")
                    else:
                        st.write("**Raw Data:**")
                        display_text_with_llm_detection(str(data), highlight_llm)
                
                with col2:
                    st.write("**File Info:**")
                    st.write(f"File: `{filename}.json`")
                    
                    if show_raw_json:
                        st.write("**Raw JSON:**")
                        st.json(data)

if __name__ == "__main__":
    main()