**Technical Documentation: Session-based Formula Calculator**

---

### Overview
The Session-based Formula Calculator is a Python application built using **Gradio** for the frontend, **SymPy** for symbolic mathematics, and **Pandas** for data management. The application enables users to create, manage, and perform calculations across multiple sessions. Results are stored in session-specific Excel files.

---

### Key Features
1. **Session Management**: Create, rename, or manage sessions, each with its own set of calculations.
2. **Dynamic Formula Input**: Input mathematical formulas dynamically and compute results.
3. **JSON-based Dynamic Input**: Supply variables for calculations in JSON format.
4. **Session Persistence**: Save and reload session data, preserving previous results.
5. **Interactive GUI**: User-friendly interface for managing sessions and performing calculations.

---

### Dependencies

- **Python Packages**:
  - `gradio`
  - `sympy`
  - `pandas`
  - `openpyxl` (for handling Excel files)
- **File System**: Stores session files locally in the `sessions` directory.

Install dependencies:
```bash
pip install gradio sympy pandas openpyxl
```

---

### Application Workflow

#### 1. **Globals and Setup**
- The global `SESSIONS_FOLDER` is created to store session files.
- Each session corresponds to an Excel file storing data and metadata.

```python
SESSIONS_FOLDER = "sessions"
if not os.path.exists(SESSIONS_FOLDER):
    os.makedirs(SESSIONS_FOLDER)
```

#### 2. **Session File Handling**
- **`get_session_file(session_name)`**:
  Returns the file path for a session Excel file.
- **`load_session_data(session_name)`**:
  Loads session data, returning stored results and metadata.
- **`save_session_data(session_name, data, last_formula, last_inputs)`**:
  Saves the updated session data and metadata.

#### 3. **Dynamic Calculations**
- **`generate_fields_and_calculate(session_name, formula, dynamic_inputs)`**:
  - Parses the formula.
  - Validates dynamic inputs.
  - Evaluates the formula with supplied inputs.
  - Updates session data and saves the result.

#### 4. **Interactive Gradio Interface**
- The Gradio interface includes:
  - **Session Management**:
    - Dropdown to select sessions.
    - Buttons to rename or create sessions.
  - **Input Fields**:
    - Textbox for formulas.
    - Textbox for dynamic inputs in JSON format.
  - **Outputs**:
    - Message label for feedback.
    - Dataframe to display results.

---

### Core Functions

#### `get_session_file`
Fetches the file path for a session file.
```python
def get_session_file(session_name):
    return os.path.join(SESSIONS_FOLDER, f"{session_name}.xlsx")
```

#### `load_session_data`
Loads existing session data and metadata. Returns:
- DataFrame of results.
- Last used formula.
- Last input variables.

#### `save_session_data`
Saves data and metadata to the session file.

#### `generate_fields_and_calculate`
Processes the formula and inputs, computes results, and updates the session.

#### Gradio Event Handlers

##### `handle_rename`
Renames the selected session file.

##### `handle_create`
Creates a new session.

##### `handle_submit`
Processes user inputs and computes the result.

##### `load_and_display_session`
Loads and displays session data in the Gradio UI.

---

### Gradio Interface Design

#### Components
1. **Session Management Accordion**:
   - Dropdown for session selection.
   - Textbox for new session names.
   - Buttons for renaming and creating sessions.
2. **Formula Input**:
   - Textbox for formula entry.
   - Textbox for JSON-based input variables.
3. **Output Area**:
   - Label for status messages.
   - Dataframe to display results.

#### Button Click Handlers
- **Rename Button**: Calls `handle_rename`.
- **Create Button**: Calls `handle_create`.
- **Submit Button**: Calls `handle_submit`.

---

### Running the Application

1. Save the script as `formula_calculator.py`.
2. Run the script:
   ```bash
   python formula_calculator.py
   ```
3. Open the Gradio interface in your web browser.

---

### Example Usage

1. Create a session named `TestSession`.
2. Enter a formula:
   ```
   Area = Length * Width
   ```
3. Provide dynamic inputs:
   ```json
   {"Length": 5, "Width": 10}
   ```
4. View results in the output table.

---

### Future Improvements

1. Enhance error handling and user feedback.
2. Add visualization features (e.g., charts).
3. Support for advanced formulas with more complex logic.
4. Implement cloud storage for session data.

---

