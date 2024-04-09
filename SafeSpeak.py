import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
import re

# API details for making requests to the Hugging Face model
API_URL = "https://api-inference.huggingface.co/models/Hate-speech-CNERG/dehatebert-mono-english"
headers = {"Authorization": "Bearer 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"}


def remove_repeating_symbols(text):
    # Regex pattern matches sequences of non-word characters (\W) that are not spaces ([^\w\s])
    # between word boundaries (\b), ensuring it only targets symbols between words.
    cleaned_text = re.sub(r'\b[^\w\s]+\b', '', text)
    return cleaned_text


# Function to detect and convert symbols to text
def symbol_detector(text):
    # Check if there are any symbols in the text
    if re.search('[^a-zA-Z0-9\\s,.\'?]', text):
        # If symbols are found, first remove repeating symbols between words
        text = remove_repeating_symbols(text)

        # Mapping of symbols/numerals to letters for further conversion
        symbol_map = {'0': 'o', '1': 'l', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b', '@': 'a', '!': 'i',
                      '$': 's'}
        # Convert input text to a list of characters, then replace each character based on the symbol_map
        output_chars = [symbol_map.get(char.lower(), char) for char in list(text)]
        # Join the characters back into a string and return it
        return ''.join(output_chars)
    else:
        # Return the original text if no symbols need conversion
        return text


# Function to make a request to the Hugging Face API with the processed text
def query(payload):
    # Send a POST request to the API with the prepared headers and payload
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


# Function to interpret the API response and display the result in the GUI
def identifier(output):
    # Extract the first result from the response (assuming the response structure matches expected format)
    first_result = output[0][0]
    label = first_result['label']
    score = first_result['score']
    # Determine the message based on the score threshold for confidence
    if score >= 0.726030:
        if label == "NON-HATE":
            label = "Offensive"
        result_text = f"We can say with confidence that this is: {label} and we are {(score * 100):.2f}% sure."
    else:
        result_text = (f"The scoring is below our confidence threshold: {score * 100: .2f}% "
                       f"\ntherefore this is Neither Hate nor Offensive.")
    # Display the result in the results display area
    results_display.config(state=tk.NORMAL)
    results_display.delete('1.0', tk.END)
    results_display.insert(tk.INSERT, result_text)
    results_display.config(state=tk.DISABLED)


# Modified Function to trigger when the 'Analyze' button is clicked
def analyze_text():
    # Retrieve text from the input box, stripping leading/trailing whitespace
    input_text = text_input.get("1.0", tk.END).strip()
    if not input_text:  # Check if the input_text is empty after stripping
        messagebox.showinfo("Invalid Input", "Please input a valid message")  # Show a popup message
        return  # Exit the function early if the input is invalid

    # Process the text for symbol detection and conversion
    convertedInput = symbol_detector(input_text)
    # Query the API with the processed text and display the result
    output = query({"inputs": convertedInput})
    identifier(output)


def exit_application():
    root.destroy()  # This method closes the Tkinter window and ends the application


def report_text():
    # Function to log the report type
    def log_report(report_type):
        reported_text = text_input.get("1.0", tk.END).strip()
        if not reported_text:  # Check if the text is empty
            messagebox.showinfo("Invalid Action", "There is no text to report.")
            return

        # Specify the file path (adjust the path as needed for your environment)
        report_file_path = "reported_texts.txt"

        # Open the file in append mode and write the report
        with open(report_file_path, "a") as file:
            file.write(f"Report Type: {report_type}, Reported Text: {reported_text}\n")

        report_window.destroy()  # Close the report window after logging
        messagebox.showinfo("Reported", "Thank you for reporting. We will review the text.")

    # Create a new window for report options
    report_window = tk.Toplevel(root)
    report_window.title("Report as...")

    # Add buttons for each report type
    tk.Button(report_window, text="Offensive", command=lambda: log_report("Offensive")).pack(fill=tk.X)
    tk.Button(report_window, text="Hateful", command=lambda: log_report("Hateful")).pack(fill=tk.X)
    tk.Button(report_window, text="Neither", command=lambda: log_report("Neither")).pack(fill=tk.X)

# Setting up the main window of the GUI application
root = tk.Tk()
root.title("Safe Speak")

# Creating and placing the text input label and box
text_input_label = tk.Label(root, text="Enter text:")
text_input_label.pack()
text_input = scrolledtext.ScrolledText(root, height=10)
text_input.pack(fill=tk.BOTH, expand=True)  # Make the text input box expand with the window

# Create a frame for the buttons to allow them to resize with the window
button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X)  # Make the frame fill the width with the window

# Creating and placing the 'Analyze' button within the frame
submit_button = tk.Button(button_frame, text="Analyze", command=analyze_text)
submit_button.pack(side=tk.LEFT, fill=tk.X, expand=True)  # Button expands and fills the frame horizontally

# Creating and placing the 'Exit' button within the frame
exit_button = tk.Button(button_frame, text="Exit", command=exit_application)
exit_button.pack(side=tk.RIGHT, fill=tk.X, expand=True)  # Button expands and fills the frame horizontally

# Creating and placing the 'Report' button within the frame
report_button = tk.Button(button_frame, text="Report", command=report_text)
report_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Creating and placing the results display area, making it expandable
results_display = scrolledtext.ScrolledText(root, height=5, state=tk.DISABLED)
results_display.pack(fill=tk.BOTH, expand=True)  # Make the results display area expand with the window

# Start the GUI event loop to listen for user interaction
root.mainloop()
