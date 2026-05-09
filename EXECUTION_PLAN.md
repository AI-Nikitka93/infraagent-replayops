# InfraAgent Execution Plan

Status legend: `PLANNED`, `IN_PROGRESS`, `DONE`, `BLOCKED`, `CANCELLED`.

1. DONE - Collect hackathon rules and judging criteria.
2. DONE - Select and later sharpen the product concept: InfraAgent ReplayOps, evidence-verified incident triage.
3. DONE - Research AMD Developer Cloud, ROCm, vLLM, Hugging Face Spaces, and tunnel topology.
4. DONE - Design LangGraph architecture and API contract.
4a. DONE - Create vLLM ROCm and Cloudflare Quick Tunnel launch scripts.
4b. DONE - Implement FastAPI and LangGraph backend with mock observability tools.
4c. DONE - Implement Hugging Face Spaces Gradio UI with polling client.
5. DONE - Run competitive review against public Lablab submissions and pivot away from weak generic incident assistant.
6. DONE - Validate mock incident scenarios and fixture format through five deterministic ReplayOps scenarios.
7. DONE - Create LangGraph state types and graph builder.
8. DONE - Implement Alert Ingestor node with runtime proof.
9. DONE - Implement Investigator node with mock observability tools.
10. DONE - Implement Root Cause Analyst node with evidence citations and optional Qwen critique.
11. DONE - Implement Runbook Generator node.
12. DONE - Implement Verification Gate node and loop controls.
13. DONE - Implement in-memory run store for polling API.
14. DONE - Implement `POST /api/triage`.
15. DONE - Implement `GET /api/status/{run_id}`.
16. DONE - Add Bearer authentication token for public API calls.
17. DONE - Create checkout deploy regression fixture.
18. DONE - Create payment dependency slowdown fixture.
19. DONE - Create resource leak, queue backlog, and vLLM saturation fixtures.
20. DONE - Add vLLM runtime proof wrapper against local OpenAI-compatible endpoint.
21. DONE - Add deterministic eval scorecard for root cause, evidence, and runbook quality.
22. DONE - Add node traces and tool-call audit output.
23. DONE - Add graceful partial-result behavior when live vLLM is unavailable.
24. DONE - Build the thin Hugging Face Spaces UI.
25. DONE - Wire UI polling to the FastAPI status endpoint with cursor support.
26. DONE - Test local graph execution without tunnel.
27. PLANNED - Test Cloudflare Tunnel from external network.
28. PLANNED - Test Hugging Face Spaces outbound call to the tunnel URL.
29. PLANNED - Record a stable demo incident script.
30. PLANNED - Create presentation narrative mapped to judging criteria.
31. PLANNED - Run end-to-end rehearsal on AMD MI300X with real vLLM/Qwen live.
32. PLANNED - Freeze demo fixtures and environment variables before submission.
