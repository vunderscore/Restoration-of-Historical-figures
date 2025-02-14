# Historical Figure Chat

A unique chatbot application that brings historical figures to life through image recognition and conversational AI. Upload an image of a historical figure, and engage in a conversation with an AI that adopts their persona and responds as they might have.

## 🌟 Features

- **Image Recognition**: Upload images of historical figures
- **Persona Adoption**: AI identifies the figure and adopts their personality
- **Interactive Chat**: Engage in meaningful conversations with historical figures
- **Real-time Responses**: Get historically contextualized answers to your questions
- **Web Search Integration**: Utilizes Tavily for accurate historical information
- **User-friendly Interface**: Built with Streamlit for a smooth user experience

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Cloud API key (for Google's Generative AI)
- Tavily API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/historical-figure-chat.git
cd historical-figure-chat
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root directory and add your API keys:
```
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided local URL (typically `http://localhost:8501`)

## 💡 How to Use

1. **Upload Image**: 
   - Click the "Upload Image" button in the sidebar
   - Select an image of a historical figure

2. **Wait for Recognition**:
   - The system will identify the historical figure in the image
   - The AI will adopt the persona of the identified figure

3. **Start Chatting**:
   - Type your questions or comments in the chat input
   - Receive responses from the AI speaking as the historical figure

4. **Start New Chat**:
   - Click "Start New Chat" in the sidebar to begin a new conversation
   - Upload a different image to chat with another historical figure

## 🛠️ Technical Architecture

The application uses several key technologies and components:

- **Streamlit**: Frontend interface and user interaction
- **LangChain & LangGraph**: Conversation workflow management
- **Google Generative AI**: Natural language processing and generation
- **Tavily**: Web search integration for accurate historical information
- **PIL (Python Imaging Library)**: Image processing and handling

## 📝 Notes

- The quality of responses depends on the clarity of the uploaded image and the historical significance of the figure
- Internet connection is required for the application to function properly
- For best results, use clear, front-facing images of well-known historical figures


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Contact

Your Name - [vishaakp@gmail.com]

Project Link: [https://github.com/yourusername/historical-figure-chat]
