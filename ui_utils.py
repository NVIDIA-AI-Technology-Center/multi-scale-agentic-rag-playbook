import gradio as gr
from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage

class ConferenceAnalysisInterface:
    def __init__(self, agent):
        self.agent = agent
        self.css = """
        .message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            white-space: pre-wrap;
            font-family: system-ui, -apple-system, sans-serif;
        }
        .message p {
            margin: 0.5em 0;
        }
        .message ul {
            margin: 0.5em 0;
            padding-left: 1.5em;
        }
        .message h2 {
            margin-top: 0;
            margin-bottom: 1em;
            color: #2a9fd6;
        }
        """
        self.demo = self._create_interface()

    def _clean_text(self, text: str) -> str:
        """Clean and format the text for better display"""
        # Replace explicit newlines and tabs with proper formatting
        text = text.replace('\\n', '\n')
        text = text.replace('\\t', '    ')  # Replace tabs with 4 spaces
        
        # Remove any double quotes at start/end if present
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
            
        # Handle any remaining escape characters
        text = text.replace('\t', '    ')  # Replace actual tab characters
        
        # Remove extra spaces at the start of lines while preserving indentation
        lines = text.splitlines()
        cleaned_lines = []
        for line in lines:
            # Keep the line's indentation but remove extra spaces
            stripped = line.rstrip()
            if stripped:  # Only add non-empty lines
                if stripped.startswith('+'):
                    # Handle bullet points with + symbol
                    stripped = '•' + stripped[1:]
                cleaned_lines.append(stripped)
        
        # Join lines back together
        text = '\n'.join(cleaned_lines)
        
        # Remove any multiple consecutive newlines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        return text

    def _process_query(self, message: str, history: List[List[str]]) -> str:
        # Convert history to messages format
        messages = []
        for h in history:
            messages.extend([
                HumanMessage(content=h[0]),
                AIMessage(content=h[1])
            ])
        
        # Add current message
        messages.append(HumanMessage(content=message))
        
        # Execute the agent
        result = self.agent.invoke({
            "messages": messages
        })
        
        # Extract the final message
        final_message = result["messages"][-1].content
        
        try:
            # Parse chain choice
            chain_start = final_message.find("Chain choice: ") + len("Chain choice: ")
            chain_end = final_message.find("\n\n")
            chain_choice = final_message[chain_start:chain_end].strip()
            
            # Parse final answer
            answer_start = final_message.find("Final answer: ") + len("Final answer: ")
            answer_text = final_message[answer_start:].strip()
            
            # If the answer is a string containing a dictionary
            if "'answer':" in answer_text:
                answer_start = answer_text.find("'answer': ") + len("'answer': ")
                answer_text = answer_text[answer_start:]
                # Remove surrounding quotes if present
                if answer_text.startswith("'") or answer_text.startswith('"'):
                    answer_text = answer_text[1:]
                if answer_text.endswith("'") or answer_text.endswith('"'):
                    answer_text = answer_text[:-1]
            
            # Clean and format the answer text
            clean_answer = self._clean_text(answer_text)
            
            # Format the final response with chain information and clean formatting
            formatted_response = f"""## Chain Used: {chain_choice}

{clean_answer}"""
            
            return formatted_response
            
        except Exception as e:
            # If parsing fails, return the original message
            return self._clean_text(final_message)

    def _create_interface(self):
        return gr.ChatInterface(
            fn=self._process_query,
            title="Conference Paper Analysis Agent",
            description="Ask questions about conference papers and abstracts. The agent will automatically route your query to the appropriate knowledge base.",
            examples=[
                "What are the main trends discussed at the conference?",
                "What are the key contributions of this paper?",
                "How does this paper's methodology compare to other works at the conference?"
            ],
            retry_btn=None,
            undo_btn=None,
            clear_btn="Clear",
            css=self.css
        )

    def launch(self, **kwargs):
        """Launch the Gradio interface with optional kwargs"""
        return self.demo.launch(**kwargs)