"""
Main GUI application using Tkinter with modern UI design
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


class ModernColors:
    """Modern color scheme for light and dark themes"""

    # Light Theme (Default)
    LIGHT_BG = "#FFFFFF"
    LIGHT_SURFACE = "#F8F9FA"
    LIGHT_SURFACE_VARIANT = "#E9ECEF"
    LIGHT_PRIMARY = "#4F46E5"  # Modern indigo
    LIGHT_PRIMARY_HOVER = "#4338CA"
    LIGHT_SUCCESS = "#10B981"  # Modern green
    LIGHT_SUCCESS_HOVER = "#059669"
    LIGHT_TEXT_PRIMARY = "#1F2937"
    LIGHT_TEXT_SECONDARY = "#6B7280"
    LIGHT_BORDER = "#E5E7EB"
    LIGHT_USER_MSG = "#4F46E5"
    LIGHT_ASSISTANT_MSG = "#10B981"

    # Dark Theme
    DARK_BG = "#1F2937"
    DARK_SURFACE = "#111827"
    DARK_SURFACE_VARIANT = "#374151"
    DARK_PRIMARY = "#6366F1"
    DARK_PRIMARY_HOVER = "#818CF8"
    DARK_SUCCESS = "#34D399"
    DARK_SUCCESS_HOVER = "#6EE7B7"
    DARK_TEXT_PRIMARY = "#F9FAFB"
    DARK_TEXT_SECONDARY = "#D1D5DB"
    DARK_BORDER = "#374151"
    DARK_USER_MSG = "#818CF8"
    DARK_ASSISTANT_MSG = "#34D399"


class ChatApplication:
    """
    Main application window for the LLM chat interface with modern UI

    This class creates and manages the Tkinter GUI, including:
    - Model selection dropdown
    - Chat display area
    - Message input field
    - Send button and new chat button
    - Modern styling with hover effects and rounded corners
    """

    def __init__(self, chat_manager: ChatManager, theme: str = "light"):
        """
        Initialize the chat application

        Args:
            chat_manager: ChatManager instance for handling chat logic
            theme: UI theme - "light" or "dark" (default: "light")
        """
        self.chat_manager = chat_manager
        self.is_processing = False
        self.theme = theme
        self.colors = ModernColors()

        # Create main window
        self.window = tk.Tk()
        self.window.title(settings.window_title)
        self.window.geometry(f"{settings.window_width}x{settings.window_height}")
        self.window.minsize(800, 600)

        # Configure window styling based on theme
        bg_color = self.colors.LIGHT_BG if theme == "light" else self.colors.DARK_BG
        self.window.configure(bg=bg_color)

        # Setup UI components
        self._setup_ui()

        # Load available models
        self._load_models()

        # Start new conversation
        self.chat_manager.start_new_conversation()

        logger.info("Chat application initialized")

    def _get_theme_colors(self):
        """Get colors based on current theme"""
        if self.theme == "dark":
            return {
                'bg': self.colors.DARK_BG,
                'surface': self.colors.DARK_SURFACE,
                'surface_variant': self.colors.DARK_SURFACE_VARIANT,
                'primary': self.colors.DARK_PRIMARY,
                'primary_hover': self.colors.DARK_PRIMARY_HOVER,
                'success': self.colors.DARK_SUCCESS,
                'success_hover': self.colors.DARK_SUCCESS_HOVER,
                'text_primary': self.colors.DARK_TEXT_PRIMARY,
                'text_secondary': self.colors.DARK_TEXT_SECONDARY,
                'border': self.colors.DARK_BORDER,
                'user_msg': self.colors.DARK_USER_MSG,
                'assistant_msg': self.colors.DARK_ASSISTANT_MSG
            }
        else:
            return {
                'bg': self.colors.LIGHT_BG,
                'surface': self.colors.LIGHT_SURFACE,
                'surface_variant': self.colors.LIGHT_SURFACE_VARIANT,
                'primary': self.colors.LIGHT_PRIMARY,
                'primary_hover': self.colors.LIGHT_PRIMARY_HOVER,
                'success': self.colors.LIGHT_SUCCESS,
                'success_hover': self.colors.LIGHT_SUCCESS_HOVER,
                'text_primary': self.colors.LIGHT_TEXT_PRIMARY,
                'text_secondary': self.colors.LIGHT_TEXT_SECONDARY,
                'border': self.colors.LIGHT_BORDER,
                'user_msg': self.colors.LIGHT_USER_MSG,
                'assistant_msg': self.colors.LIGHT_ASSISTANT_MSG
            }

    def _setup_ui(self) -> None:
        """Create and layout all UI components with modern styling"""
        colors = self._get_theme_colors()

        # ============= TOP TOOLBAR (MODERN DESIGN) =============
        toolbar = tk.Frame(self.window, bg=colors['surface'], height=70)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        toolbar.pack_propagate(False)

        # Left section - Model selector
        left_section = tk.Frame(toolbar, bg=colors['surface'])
        left_section.pack(side=tk.LEFT, padx=20, pady=15)

        # Model selector label
        model_label = tk.Label(
            left_section,
            text="Model",
            bg=colors['surface'],
            fg=colors['text_secondary'],
            font=("Segoe UI", 10)
        )
        model_label.pack(side=tk.LEFT, padx=(0, 10))

        # Model dropdown with modern styling
        self.model_var = tk.StringVar(value=settings.default_model)

        # Style for combobox
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Modern.TCombobox',
            fieldbackground=colors['bg'],
            background=colors['surface_variant'],
            foreground="black" if self.theme == "dark" else colors['text_primary'],
            borderwidth=1,
            relief='solid',
            padding=8
        )

        self.model_selector = ttk.Combobox(
            left_section,
            textvariable=self.model_var,
            state="readonly",
            width=25,
            style='Modern.TCombobox',
            font=("Segoe UI", 10)
        )
        self.model_selector.pack(side=tk.LEFT)
        self.model_selector.bind("<<ComboboxSelected>>", self._on_model_change)

        # Right section - Theme toggle and New chat button
        right_section = tk.Frame(toolbar, bg=colors['surface'])
        right_section.pack(side=tk.RIGHT, padx=20, pady=15)

        # Theme toggle button
        self.theme_btn = tk.Button(
            right_section,
            text="🌙 Dark" if self.theme == "light" else "☀️ Light",
            command=self._toggle_theme,
            bg=colors['surface_variant'],
            fg="black" if self.theme == "dark" else colors['text_primary'],
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            borderwidth=0
        )
        self.theme_btn.pack(side=tk.LEFT, padx=(0, 10))
        self._add_button_hover(self.theme_btn, colors['surface_variant'], colors['border'])

        # New chat button with modern primary style
        self.new_chat_btn = tk.Button(
            right_section,
            text="✨ New Chat",
            command=self._on_new_chat,
            bg=colors['primary'],
            fg="black",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            borderwidth=0
        )
        self.new_chat_btn.pack(side=tk.LEFT)
        self._add_button_hover(self.new_chat_btn, colors['primary'], colors['primary_hover'])

        # ============= CHAT DISPLAY AREA (MODERN CARD DESIGN) =============
        # Container with padding
        chat_container = tk.Frame(self.window, bg=colors['bg'])
        chat_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Chat frame (card style)
        chat_frame = tk.Frame(
            chat_container,
            bg=colors['surface'],
            highlightbackground=colors['border'],
            highlightthickness=1
        )
        chat_frame.pack(fill=tk.BOTH, expand=True)

        # Scrolled text widget with modern styling
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Segoe UI", 11),
            bg=colors['surface'],
            fg=colors['text_primary'],
            relief=tk.FLAT,
            padx=20,
            pady=20,
            borderwidth=0,
            insertbackground=colors['primary']
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for modern styling
        self.chat_display.tag_config(
            "user",
            foreground=colors['user_msg'],
            font=("Segoe UI", 12, "bold"),
            spacing1=10
        )
        self.chat_display.tag_config(
            "assistant",
            foreground=colors['assistant_msg'],
            font=("Segoe UI", 12, "bold"),
            spacing1=10
        )
        self.chat_display.tag_config(
            "message",
            foreground=colors['text_primary'],
            font=("Segoe UI", 11),
            spacing1=5,
            spacing3=10
        )
        self.chat_display.tag_config(
            "separator",
            foreground=colors['border']
        )

        # Make chat display read-only
        self.chat_display.config(state=tk.DISABLED)

        # ============= INPUT AREA (MODERN DESIGN) =============
        input_container = tk.Frame(self.window, bg=colors['bg'])
        input_container.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))

        # Input frame with card styling
        input_frame = tk.Frame(
            input_container,
            bg=colors['surface'],
            highlightbackground=colors['border'],
            highlightthickness=1
        )
        input_frame.pack(fill=tk.X)

        # Message input field with modern styling
        self.message_input = tk.Text(
            input_frame,
            height=3,
            width=80,
            font=("Segoe UI", 11),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg=colors['surface'],
            fg=colors['text_primary'],
            padx=15,
            pady=15,
            borderwidth=0,
            insertbackground=colors['primary']
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind Enter key to send message
        self.message_input.bind("<Return>", self._on_enter_key)

        # Send button container
        button_container = tk.Frame(input_frame, bg=colors['surface'])
        button_container.pack(side=tk.RIGHT, padx=15, pady=15)

        # Send button with modern success color
        self.send_btn = tk.Button(
            button_container,
            text="Send →",
            command=self._on_send,
            bg=colors['success'],
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=25,
            pady=12,
            borderwidth=0
        )
        self.send_btn.pack()
        self._add_button_hover(self.send_btn, colors['success'], colors['success_hover'])

        # Focus on input field
        self.message_input.focus()

    def _add_button_hover(self, button, normal_color, hover_color):
        """Add hover effect to button"""
        def on_enter(e):
            if button['state'] != 'disabled':
                button.config(bg=hover_color)

        def on_leave(e):
            if button['state'] != 'disabled':
                button.config(bg=normal_color)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def _toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme = "dark" if self.theme == "light" else "light"

        # Save current conversation state
        messages = self.chat_manager.get_messages()

        # Rebuild UI with new theme
        for widget in self.window.winfo_children():
            widget.destroy()

        self._setup_ui()

        # Restore conversation
        if messages:
            self.chat_display.config(state=tk.NORMAL)
            for msg in messages:
                sender = "You" if msg.role == Role.USER else "Assistant"
                tag = "user" if msg.role == Role.USER else "assistant"
                self._display_message(sender, msg.content, tag)
            self.chat_display.config(state=tk.DISABLED)

        self._load_models()
        logger.info(f"Theme switched to {self.theme}")

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

        # Send message in background thread
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
        Enable or disable input controls with visual feedback

        Args:
            enabled: True to enable, False to disable
        """
        colors = self._get_theme_colors()
        state = tk.NORMAL if enabled else tk.DISABLED

        self.message_input.config(state=state)
        self.send_btn.config(state=state)

        # Visual feedback for disabled state
        if not enabled:
            self.send_btn.config(bg=colors['border'])
        else:
            self.send_btn.config(bg=colors['success'])
            self.message_input.focus()

    def run(self) -> None:
        """Start the Tkinter main event loop"""
        logger.info("Starting GUI main loop")
        self.window.mainloop()
