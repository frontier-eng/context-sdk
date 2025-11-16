from google import genai
from google.genai import types
import json
import uuid
import time
from typing import Dict, Any, List, Optional
from .config import settings


class GeminiService:
    """Service for managing Gemini File Search store."""
    
    def __init__(self):
        self.client: Optional[genai.Client] = None
        self.store_name: Optional[str] = None
        self.initialized = False
    
    def initialize(self):
        """Initialize Gemini client and create/get File Search store."""
        if self.initialized:
            return
        
        self.client = genai.Client(api_key=settings.gemini_api_key)
        
        # Create or get the global File Search store
        try:
            # Try to list stores and find existing one
            stores = self.client.file_search_stores.list()
            if stores and len(stores) > 0:
                # Use the first store (global store)
                self.store_name = stores[0].name
            else:
                # Create new store
                store = self.client.file_search_stores.create(
                    config={'display_name': 'context-api-global-store'}
                )
                self.store_name = store.name
        except Exception as e:
            # If list doesn't work, try creating directly
            try:
                store = self.client.file_search_stores.create(
                    config={'display_name': 'context-api-global-store'}
                )
                self.store_name = store.name
            except Exception:
                # If creation fails, we'll handle it on first use
                pass
        
        self.initialized = True
    
    def store_trace(self, user_id: str, trace_data: Dict[str, Any]) -> str:
        """Store a trace in Gemini File Search with user_id namespacing."""
        if not self.initialized or not self.client:
            raise RuntimeError("Gemini service not initialized")
        
        # Add user_id to trace data for namespacing
        trace_data["user_id"] = user_id
        trace_id = str(uuid.uuid4())
        trace_data["trace_id"] = trace_id
        
        # Convert to JSON string
        trace_json = json.dumps(trace_data, default=str)
        
        # Create a temporary file
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(trace_json)
            temp_path = f.name
        
        try:
            # Upload to File Search store
            operation = self.client.file_search_stores.upload_to_file_search_store(
                file=temp_path,
                file_search_store_name=self.store_name,
                config={
                    'display_name': f'trace_{user_id}_{trace_id}',
                }
            )
            
            # Wait for operation to complete
            while not operation.done:
                time.sleep(1)
                operation = self.client.operations.get(operation)
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return trace_id
    
    def retrieve_context(self, user_id: str, prompt: str, model: str, max_results: int = 5) -> Dict[str, Any]:
        """Retrieve relevant context from traces for a given prompt."""
        if not self.initialized or not self.client:
            raise RuntimeError("Gemini service not initialized")
        
        # Create a query that includes user_id filtering
        query = f"user_id: {user_id}\n\nFind similar prompts and successful patterns for: {prompt}"
        
        try:
            # Query the File Search store
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[{
                        "file_search": {
                            "file_search_store_names": [self.store_name]
                        }
                    }]
                )
            )
            
            # Extract relevant traces from grounding metadata
            relevant_traces = []
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    grounding = candidate.grounding_metadata
                    if hasattr(grounding, 'retrieval_queries'):
                        # Extract file references
                        for query_result in getattr(grounding, 'retrieval_queries', []):
                            if hasattr(query_result, 'relevant_chunks'):
                                for chunk in query_result.relevant_chunks:
                                    relevant_traces.append({
                                        "chunk": getattr(chunk, 'chunk', {}),
                                        "relevance_score": getattr(chunk, 'relevance_score', 0.0)
                                    })
            
            # Get the enhanced context from the response
            enhanced_context = response.text if hasattr(response, 'text') else ""
            
            # Generate suggestions based on retrieved traces
            suggestions = {
                "similar_prompts_found": len(relevant_traces),
                "model": model,
                "recommendations": []
            }
            
            return {
                "enhanced_context": enhanced_context,
                "relevant_traces": relevant_traces[:max_results],
                "suggestions": suggestions
            }
            
        except Exception as e:
            # Fallback if retrieval fails
            return {
                "enhanced_context": prompt,
                "relevant_traces": [],
                "suggestions": {
                    "error": str(e),
                    "model": model
                }
            }


gemini_service = GeminiService()

