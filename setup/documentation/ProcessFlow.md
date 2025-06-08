# 📋 AI-Assisted Interview Process (Full Workflow)

## Interviewer Responsibilities (Before the Interview)

1. **Design Rubric**
   - Create a skills assessment rubric in `.csv` format.
   - Format must be readable and structured for LLM parsing.

2. **Prepare API Access**
   - Obtain a valid OpenAI API key.
   - Store the key securely in the `.env` file (e.g., `OPENAI_API_KEY=...`).

3. **Launch Flask Application**
   - Ensure Flask server is running locally (`server.py`).
   - Verify required directories exist:
     - `instance/rubrics/`
     - `instance/transcripts/`
     - `instance/logs/`

---

## Interviewee Flow (SkillScope User)

1. **Access Login Page**
   - Entry point: [`login.html`](login.html).
   - No authentication required; unique ID restricts repeat attempts.

2. **Begin Interview**
   - 60-minute countdown timer starts automatically.
   - Timer is visible on-screen and in the browser tab title.

3. **Record Audio**
   - Only one recording session permitted.
   - Audio is saved in `.webm` format under `/uploaded_audio`.

4. **Preview Transcript**
   - Transcript is generated via OpenAI Whisper.
   - Displayed for user review (not editable).

5. **Add Reflection**
   - Optional field to enter self-reflection after the interview.
   - Reflections are excluded from AI evaluation.

6. **Submit for Evaluation**
   - Transcript package is finalized and submitted.
   - Becomes available in the interviewer dashboard.

---

## Interviewer Evaluation Workflow

1. **Access Interviewer Dashboard**
   - Entry point: [`interviewer.html`](interviewer.html)

2. **Upload or Select Rubric**
   - Upload rubric as `.csv`; contents previewed.
   - Rubric is retained in memory for use with selected transcripts.

3. **Load Available Transcripts**
   - Automatically fetches all unprocessed transcript entries.
   - Each entry appears as a selectable button with name + date.

4. **Select Transcripts**
   - Toggle buttons to select/deselect transcripts.
   - “Select All” button available.
   - Selected buttons change color for visibility.

5. **Preview Transcripts**
   - Single selection: Full transcript shown.
   - Multiple selection: Summary list of names and timestamps.

6. **Submit to LLM**
   - Each selected transcript is:
     - Bundled with the current rubric.
     - Sent to OpenAI using API key in `.env`.
   - LLM returns evaluation text for each submission.

7. **Log Submission**
   - All submission events are appended to `instance/logs/skillscope.log`.
   - Once evaluated, buttons are disabled to prevent duplicate submission.

8. **Review AI Feedback**
   - Interviewer reviews LLM output.
   - Validates whether the evaluation aligns with the rubric and transcript content.
   - Manual review is required before final feedback is acted upon or exported.

---

