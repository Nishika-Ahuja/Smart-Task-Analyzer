from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import InputTaskSerializer
from .scoring import compute_scores, CircularDependencyError


class AnalyzeView(APIView):
    def post(self, request):
        payload = request.data
        
        tasks = payload.get("tasks")
        if not tasks:
        
            tasks = payload if isinstance(payload, list) else [payload]
      
        strategy = (
            payload.get("strategy") or 
            request.query_params.get("strategy") or 
            "smart"
        )
        
      
        valid_strategies = ["smart", "fast", "impact", "deadline"]
        if strategy not in valid_strategies:
            strategy = "smart"
        
        print(f"[AnalyzeView] Received strategy: {strategy}")  
        print(f"[AnalyzeView] Number of tasks: {len(tasks)}")  
        
    
        weights = payload.get("weights", None)
        
       
        validated = []
        errors = []
        for idx, t in enumerate(tasks):
            s = InputTaskSerializer(data=t)
            if not s.is_valid():
                errors.append({"index": idx, "errors": s.errors})
            else:
                validated.append(s.validated_data)
        
        if errors:
            return Response(
                {"detail": "Validation errors", "errors": errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            results = compute_scores(validated, strategy=strategy, weights=weights)
        except CircularDependencyError as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"[AnalyzeView] Returning {len(results)} scored tasks")  
        
        return Response(
            {
                "strategy": strategy,
                "tasks": results
            }, 
            status=status.HTTP_200_OK
        )


class SuggestView(APIView):
    def post(self, request):
        return self._process_request(request)
    
    def get(self, request):
        return self._process_request(request)
    
    def _process_request(self, request):
    
        tasks = request.data.get("tasks") if request.data else None
        
        if not tasks:
            tasks_param = request.query_params.get("tasks")
            if tasks_param:
                try:
                    import json
                    tasks = json.loads(tasks_param)
                except Exception:
                    return Response(
                        {"detail": "Could not parse tasks query parameter"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        if not tasks:
            return Response(
                {"detail": "No tasks provided. Send tasks in the request body."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        strategy = (
            request.data.get("strategy") if request.data else None or
            request.query_params.get("strategy") or 
            "smart"
        )
  
        valid_strategies = ["smart", "fast", "impact", "deadline"]
        if strategy not in valid_strategies:
            strategy = "smart"
        
        print(f"[SuggestView] Received strategy: {strategy}")  
        
        validated = []
        errors = []
        for idx, t in enumerate(tasks):
            s = InputTaskSerializer(data=t)
            if not s.is_valid():
                errors.append({"index": idx, "errors": s.errors})
            else:
                validated.append(s.validated_data)
        
        if errors:
            return Response(
                {"detail": "Validation errors", "errors": errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
    
        try:
            scored = compute_scores(validated, strategy=strategy)
        except CircularDependencyError as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        top3 = scored[:3] 
        
        suggestions = []
        for t in top3:
            parts = t.get("explanation", "").split(",")
            values = {}
            for part in parts:
                if ":" in part:
                    k, v = part.strip().split(":")
                    try:
                        values[k.strip()] = float(v)
                    except:
                        pass
            
            dominant = max(values.items(), key=lambda x: x[1])[0] if values else "score"
            
            suggestions.append({
                "id": t["id"],
                "title": t["title"],
                "score": t["score"],
                "reason": t.get("reason", f"High {dominant} -> {values.get(dominant, 0):.2f}")
            })
        
        return Response(
            {
                "strategy": strategy, 
                "suggestions": suggestions
            }, 
            status=status.HTTP_200_OK
        )