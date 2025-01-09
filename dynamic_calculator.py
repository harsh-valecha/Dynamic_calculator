import gradio as gr
import sympy as sp
import pandas as pd
import os

# Globals
SESSIONS_FOLDER = "sessions"
if not os.path.exists(SESSIONS_FOLDER):
    os.makedirs(SESSIONS_FOLDER)


# Function to handle session file
def get_session_file(session_name):
    return os.path.join(SESSIONS_FOLDER, f"{session_name}.xlsx")


# Load or create session data
def load_session_data(session_name):
    file_path = get_session_file(session_name)
    if os.path.exists(file_path):
        with pd.ExcelFile(file_path) as xls:
            data = pd.read_excel(xls, sheet_name=0)
            metadata = pd.read_excel(xls, sheet_name="Metadata") if "Metadata" in xls.sheet_names else None
            last_formula = metadata.iloc[0]["LastFormula"] if metadata is not None else ""
            last_inputs = metadata.iloc[0]["LastInputs"] if metadata is not None else "{}"
        return data, last_formula, last_inputs
    else:
        return pd.DataFrame(), "", "{}"


def save_session_data(session_name, data, last_formula=None, last_inputs=None):
    file_path = get_session_file(session_name)
    with pd.ExcelWriter(file_path) as writer:
        data.to_excel(writer, index=False)
        if last_formula or last_inputs:
            metadata = pd.DataFrame({"LastFormula": [last_formula], "LastInputs": [last_inputs]})
            metadata.to_excel(writer, index=False, sheet_name="Metadata")


# Function to dynamically generate fields and calculate results
def generate_fields_and_calculate(session_name, formula, dynamic_inputs):
    try:
        # Parse the formula
        lhs, rhs = formula.split("=")
        lhs = lhs.strip().lower()  # Ensure the LHS is lowercase
        rhs = sp.sympify(rhs.strip())

        # Extract variables from the formula and convert them to lowercase
        variables = [str(var).lower() for var in rhs.free_symbols]

        # Parse dynamic inputs and normalize keys to lowercase
        try:
            inputs = {str(k).lower(): v for k, v in eval(dynamic_inputs).items()} if dynamic_inputs else {}
        except Exception as e:
            return f"Invalid input format: {e}", None, False

        # Check if all variables have been provided
        subs = {var: inputs.get(var, None) for var in variables}
        if None in subs.values():
            missing_vars = [var for var, val in subs.items() if val is None]
            return f"Missing values for: {', '.join(missing_vars)}", None, False

        # Calculate the result
        result = rhs.evalf(subs=subs)

        # Load current session data (extract only the DataFrame part)
        session_data, _, _ = load_session_data(session_name)

        # Prepare the DataFrame dynamically
        columns = variables + [lhs]  # Variables + calculated column
        values = [inputs[var] for var in variables] + [float(result)]  # Values in order

        # Append the new result
        new_row = pd.DataFrame([values], columns=columns)
        updated_data = pd.concat([session_data, new_row], ignore_index=True)
        # Ensure 'Insertion Order' exists before sorting
        if 'Insertion Order' not in updated_data.columns:
            updated_data["Insertion Order"] = range(1, len(updated_data) + 1)
        else:
            updated_data = updated_data.sort_values(by='Insertion Order', ascending=False).reset_index(drop=True)
            updated_data["Insertion Order"] = range(1, len(updated_data) + 1)

        # Save updated data with metadata
        save_session_data(session_name, updated_data, last_formula=formula, last_inputs=dynamic_inputs)

        return "Calculation successful!", updated_data.drop(columns=["Insertion Order"]), True
    except Exception as e:
        return f"Error: {str(e)}", None, False


# Gradio interface
def create_interface():
    with gr.Blocks() as app:
        gr.Markdown("## Session-based Formula Calculator")

        # Session management inside a slider window
        with gr.Accordion("Manage Sessions", open=False):
            session_dropdown = gr.Dropdown(
                label="Select Session",
                choices=[f.split(".")[0] for f in os.listdir(SESSIONS_FOLDER) if f.endswith(".xlsx")],
                value=None,
                interactive=True
            )
            session_name_input = gr.Textbox(label="Rename or Create Session", placeholder="Enter session name")
            with gr.Row():
                rename_btn = gr.Button("Rename Session")
                create_btn = gr.Button("Create New Session")

            session_message = gr.Label(label="Session Status")

        # Inputs
        with gr.Row():
            formula_input = gr.Textbox(label="Enter Formula (e.g., Speed = Distance / Time)",
                                       placeholder="Enter your formula here")
        with gr.Row():
            dynamic_inputs = gr.Textbox(label="Dynamic Inputs (JSON format, e.g., {'distance': 10, 'time': 2})")

        # Outputs
        output_message = gr.Label(label="Message")
        output_table = gr.Dataframe(label="Results", interactive=False, visible=False)

        # Handlers
        def handle_rename(current_session, new_name):
            if not current_session:
                return gr.update(), "Please select a session to rename."

            if not new_name:
                return gr.update(), "Please provide a new session name."

            sessions = [f.split(".")[0] for f in os.listdir(SESSIONS_FOLDER) if f.endswith(".xlsx")]

            if new_name in sessions:
                return gr.update(), "Session name already exists. Please provide a unique name."

            if current_session == new_name:
                return gr.update(), "The new name is the same as the current name. Please provide a different name."

            # Rename session
            old_file = get_session_file(current_session)
            new_file = get_session_file(new_name)

            if os.path.exists(old_file):
                os.rename(old_file, new_file)

            sessions = [f.split(".")[0] for f in os.listdir(SESSIONS_FOLDER) if f.endswith(".xlsx")]
            return gr.update(choices=sessions, value=new_name), f"Session renamed to '{new_name}' successfully!"

        def handle_create(new_name):
            if not new_name:
                return gr.update(), "Please provide a session name."

            sessions = [f.split(".")[0] for f in os.listdir(SESSIONS_FOLDER) if f.endswith(".xlsx")]

            if new_name in sessions:
                return gr.update(), "Session name already exists. Please provide a unique name."

            # Create new session
            new_file = get_session_file(new_name)
            pd.DataFrame().to_excel(new_file, index=False)

            sessions = [f.split(".")[0] for f in os.listdir(SESSIONS_FOLDER) if f.endswith(".xlsx")]
            return gr.update(choices=sessions, value=new_name), f"Session '{new_name}' created successfully!"

        def handle_submit(session_dropdown, formula, dynamic_inputs):
            if not session_dropdown:
                return "Please select a session.", None, False
            message, data, success = generate_fields_and_calculate(session_dropdown, formula, dynamic_inputs)
            if success:
                return message, gr.update(value=data, visible=True)
            else:
                return message, gr.update(value=None, visible=False)

        # Events
        rename_btn.click(
            handle_rename,
            [session_dropdown, session_name_input],
            [session_dropdown, session_message]
        )

        create_btn.click(
            handle_create,
            [session_name_input],
            [session_dropdown, session_message]
        )

        # Modify session dropdown change to load and display session data
        def load_and_display_session(session_name):
            if session_name:
                session_data, last_formula, last_inputs = load_session_data(session_name)
                if not session_data.empty:
                    session_data = session_data.drop(columns=["Insertion Order"], errors="ignore").sort_index(
                        ascending=False)
                    return session_data, "Session loaded successfully.", gr.update(
                        visible=True), last_formula, last_inputs
                else:
                    return pd.DataFrame(), "Session is empty.", gr.update(visible=False), "", "{}"
            else:
                return pd.DataFrame(), "Please select a valid session.", gr.update(visible=False), "", "{}"

        # Connect the session dropdown change event
        session_dropdown.change(
            lambda session_name: load_and_display_session(session_name),
            [session_dropdown],
            [output_table, session_message, output_table, formula_input, dynamic_inputs]
        )

        submit_btn = gr.Button("Calculate")
        submit_btn.click(handle_submit, [session_dropdown, formula_input, dynamic_inputs],
                         [output_message, output_table])

    return app


# Run the app
if __name__ == "__main__":
    app = create_interface()
    app.launch()