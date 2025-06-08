```mermaid
graph TD

%% ===== UI Pages =====
subgraph UI_Pages
  A1[index.html]
  A2[login.html]
  A3[interview.html]
  A4[interviewer.html]
  A5[evaluate.html]
end

%% ===== JavaScript Functions =====
subgraph JS_Functions
  J1["startRecording"]
  J2["stopRecording"]
  J3["parseRubric"]
  J4["fetchTranscripts"]
  J5["displayTranscript"]
  J6["submitSelectedTranscripts"]
  J7["selectAllTranscripts"]
end

%% ===== Flask Routes =====
subgraph Flask_Routes
  F1["GET /"]
  F2["GET /transcripts"]
  F3["POST /evaluate-transcript"]
  F4["POST /upload-audio"]
  F5["POST /transcribe"]
end

%% ===== Data Assets =====
subgraph Data_Storage
  D1[transcripts.jsonl]
  D2[test_rubric.csv]
  D3[uploaded_audio/*.webm]
  D4[.env API Key]
end

%% ===== Page Navigation =====
A1 --> A2
A1 --> A4
A1 --> A5
A2 --> A3
A4 --> A5

%% ===== Frontend-Backend Interactions =====
A3 --> J1
A3 --> J2
A4 --> J3
A4 --> J4
A4 --> J5
A4 --> J6
A4 --> J7

J4 --> F2
J6 --> F3
J1 --> F4
J2 --> F5
J3 --> D2
F2 --> D1
F3 --> D4
F4 --> D3
F5 --> D3
