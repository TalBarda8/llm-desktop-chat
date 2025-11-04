"""
Main GUI application using Tkinter
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import List
from ..core.chat_manager import ChatManager
from ..core.message import Role
from ..config.settings import settings
from ..utils.logger import setup_logger
import threading

logger = setup_logger("gui", "logs/app.log")


class ChatApplication:
    """
    Main application window for the LLM chat interface

    This class creates and manages the Tkinter GUI, including:
    - Model selection dropdown
    - Chat display area
    - Message input field
    - Send button and new chat button
    """

    def __init__(self, chat_manager: ChatManager):
        """
        Initialize the chat application

        Args:
            chat_manager: ChatManager instance for handling chat logic
        """
        self.chat_manager = chat_manager
        self.is_processing = False  # Flag to prevent multiple simultaneous requests

        # Create main window
        self.window = tk.Tk()
        self.window.title(settings.window_title)
        self.window.geometry(f"{settings.window_width}x{settings.window_height}")

        # Configure window styling
        self.window.configure(bg="#f0f0f0")

        # Setup UI components
        self._setup_ui()

        # Load available models
        self._load_models()

        # Start new conversation
        self.chat_manager.start_new_conversation()

        logger.info("Chat application initialized")

    def _setup_ui(self) -> None:
        """Create and layout all UI components"""

        # ============= TOP TOOLBAR =============
        toolbar = tk.Frame(self.window, bg="#2c3e50", height=50)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)

        # Model selector label
        model_label = tk.Label(
            toolbar,
            text="Model:",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 10)
        )
        model_label.pack(side=tk.LEFT, padx=(10, 5), pady=10)

        # Model dropdown
        self.model_var = tk.StringVar(value=settings.default_model)
        self.model_selector = ttk.Combobox(
            toolbar,
            textvariable=self.model_var,
            state="readonly",
            width=20
        )
        self.model_selector.pack(side=tk.LEFT, padx=5, pady=10)
        self.model_selector.bind("<<ComboboxSelected>>", self._on_model_change)

        # New chat button
        self.new_chat_btn = tk.Button(
            toolbar,
            text="New Chat",
            command=self._on_new_chat,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        self.new_chat_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # ============= CHAT DISPLAY AREA =============
        chat_frame = tk.Frame(self.window, bg="white")
        chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrolled text widget for displaying chat messages
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Arial", 11),
            bg="white",
            fg="#2c3e50",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for styling different message types
        self.chat_display.tag_config("user", foreground="#2980b9", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("assistant", foreground="#27ae60", font=("Arial", 11, "bold"))
        self.chat_display.tag_config("message", foreground="#2c3e50", font=("Arial", 11))
        self.chat_display.tag_config("separator", foreground="#bdc3c7")

        # Make chat display read-only
        self.chat_display.config(state=tk.DISABLED)

        # ============= INPUT AREA =============
        input_frame = tk.Frame(self.window, bg="#ecf0f1", height=100)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

        # Message input field
        self.message_input = tk.Text(
            input_frame,
            height=3,
            width=80,
            font=("Arial", 11),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Bind Enter key to send message (Shift+Enter for new line)
        self.message_input.bind("<Return>", self._on_enter_key)

        # Send button
        self.send_btn = tk.Button(
            input_frame,
            text="Send",
            command=self._on_send,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            width=10,
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=10
        )
        self.send_btn.pack(side=tk.RIGHT)

        # Focus on input field
        self.message_input.focus()

    def _load_models(self) -> None:
        """Load available models from Ollama and populate dropdown"""
        try:
            models = self.chat_manager.client.list_models()
            if models:
                self.model_selector["values"] = models
                # Set first model as default if current model not in list
                if self.model_var.get() not in models:
                    self.model_var.set(models[0])
                    self.chat_manager.set_model(models[0])
                logger.info(f"Loaded {len(models)} models")
            else:
                logger.warning("No models found")
                messagebox.showwarning(
                    "No Models",
                    "No models found in Ollama. Please pull a model first."
                )
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            messagebox.showerror("Error", f"Failed to load models: {e}")

    def _on_model_change(self, event=None) -> None:
        """Handle model selection change"""
        selected_model = self.model_var.get()
        self.chat_manager.set_model(selected_model)
        logger.info(f"User selected model: {selected_model}")

    def _on_new_chat(self) -> None:
        """Handle new chat button click"""
        if self.is_processing:
            messagebox.showinfo("Please Wait", "Please wait for current response to complete")
            return

        # Clear chat display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)

        # Start new conversation
        self.chat_manager.start_new_conversation()
        logger.info("New chat started")

    def _on_enter_key(self, event) -> str:
        """
        Handle Enter key press in message input

        Enter: Send message
        Shift+Enter: New line
        """
        if event.state & 0x1:  # Shift key is pressed
            return None  # Allow default behavior (new line)
        else:
            self._on_send()
            return "break"  # Prevent default behavior (new line)

    def _on_send(self) -> None:
        """Handle send button click or Enter key press"""
        # Get message text
        message = self.message_input.get(1.0, tk.END).strip()

        # Validate input
        if not message:
            return

        if self.is_processing:
            messagebox.showinfo("Please Wait", "Please wait for current response to complete")
            return

        # Clear input field
        self.message_input.delete(1.0, tk.END)

        # Display user message
        self._display_message("You", message, "user")

        # Disable input while processing
        self._set_input_enabled(False)
        self.is_processing = True

        # Send message in background thread to prevent UI freezing
        thread = threading.Thread(
            target=self._send_message_async,
            args=(message,),
            daemon=True
        )
        thread.start()

    def _send_message_async(self, message: str) -> None:
        """
        Send message to API in background thread

        Args:
            message: User's message text
        """
        try:
            # Prepare for streaming response
            self._prepare_assistant_message()

            # Send message and receive streaming response
            self.chat_manager.send_message(
                message,
                on_chunk=self._on_response_chunk
            )

            # Finalize response display
            self._finalize_assistant_message()

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.window.after(0, lambda: messagebox.showerror(
                "Error",
                f"Failed to send message: {e}"
            ))
        finally:
            # Re-enable input
            self.window.after(0, lambda: self._set_input_enabled(True))
            self.is_processing = False

    def _prepare_assistant_message(self) -> None:
        """Prepare chat display for streaming assistant response"""
        def update():
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, "\nAssistant:\n", "assistant")
            self.chat_display.insert(tk.END, "", "message")
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.see(tk.END)

        self.window.after(0, update)

    def _on_response_chunk(self, chunk: str) -> None:
        """
        Handle each chunk of streaming response

        Args:
            chunk: Text chunk from API
        """
        def update():
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, chunk, "message")
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.see(tk.END)

        # Schedule UI update on main thread
        self.window.after(0, update)

    def _finalize_assistant_message(self) -> None:
        """Finalize assistant message display"""
        def update():
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, "\n", "message")
            self.chat_display.insert(tk.END, "-" * 80 + "\n", "separator")
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.see(tk.END)

        self.window.after(0, update)

    def _display_message(self, sender: str, message: str, tag: str) -> None:
        """
        Display a message in the chat area

        Args:
            sender: Message sender name (e.g., "You", "Assistant")
            message: Message text
            tag: Text tag for styling
        """
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"\n{sender}:\n", tag)
        self.chat_display.insert(tk.END, f"{message}\n", "message")
        self.chat_display.insert(tk.END, "-" * 80 + "\n", "separator")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def _set_input_enabled(self, enabled: bool) -> None:
        """
        Enable or disable input controls

        Args:
            enabled: True to enable, False to disable
        """
        state = tk.NORMAL if enabled else tk.DISABLED
        self.message_input.config(state=state)
        self.send_btn.config(state=state)

        if enabled:
            self.message_input.focus()

    def run(self) -> None:
        """Start the Tkinter main event loop"""
        logger.info("Starting GUI main loop")
        self.window.mainloop()
