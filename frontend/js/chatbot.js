// Chatbot Functionality

const chatbotToggle = document.getElementById('chatbot-toggle');
const chatbotContainer = document.getElementById('chatbot-container');
const chatbotClose = document.getElementById('chatbot-close');
const chatbotInput = document.getElementById('chatbot-input');
const chatbotSend = document.getElementById('chatbot-send');
const chatbotMessages = document.getElementById('chatbot-messages');

// Toggle chatbot
chatbotToggle.addEventListener('click', function() {
    chatbotContainer.classList.toggle('chatbot-closed');
});

chatbotClose.addEventListener('click', function() {
    chatbotContainer.classList.add('chatbot-closed');
});

// Send message
function sendMessage() {
    const message = chatbotInput.value.trim();
    
    if (!message) return;
    
    // Add user message
    addMessage(message, 'user');
    chatbotInput.value = '';
    
    // Simulate bot response
    setTimeout(() => {
        const response = getBotResponse(message);
        addMessage(response, 'bot');
    }, 500);
}

chatbotSend.addEventListener('click', sendMessage);
chatbotInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Add message to chat
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = text;
    chatbotMessages.appendChild(messageDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

// Simple rule-based bot responses
function getBotResponse(message) {
    const lowerMessage = message.toLowerCase();
    
    // Preterm related queries
    if (lowerMessage.includes('preterm') || lowerMessage.includes('premature')) {
        return 'Preterm birth occurs before 37 weeks of pregnancy. Risk factors include previous preterm births, multiple pregnancies, high blood pressure, and diabetes. Our AI model analyzes EHG signals and clinical data to assess your risk.';
    }
    
    // Acidemia related queries
    if (lowerMessage.includes('acidemia') || lowerMessage.includes('fetal')) {
        return 'Fetal acidemia is a condition where the baby has too much acid in their blood during labor. It can be detected through CTG monitoring of fetal heart rate. Early detection is crucial for preventing complications.';
    }
    
    // EHG queries
    if (lowerMessage.includes('ehg') || lowerMessage.includes('electrohysterogram')) {
        return 'EHG (Electrohysterogram) measures the electrical activity of the uterus. It helps predict preterm labor by analyzing uterine contraction patterns. Upload a .dat signal file in the Doctor Portal for analysis.';
    }
    
    // CTG queries
    if (lowerMessage.includes('ctg') || lowerMessage.includes('cardiotocography')) {
        return 'CTG (Cardiotocography) monitors fetal heart rate and uterine contractions. It helps detect fetal distress and acidemia during pregnancy and labor. Upload a .dat signal file in the Doctor Portal for analysis.';
    }
    
    // How to use
    if (lowerMessage.includes('how') || lowerMessage.includes('use')) {
        return 'For doctors: Upload .dat signal files (EHG or CTG) for advanced AI analysis. For patients: Fill in your medical details in the form for risk assessment. Both methods provide personalized recommendations.';
    }
    
    // Risk factors
    if (lowerMessage.includes('risk') || lowerMessage.includes('factor')) {
        return 'Common risk factors include: maternal age (<20 or >35), previous preterm births, multiple pregnancies, high blood pressure, diabetes, smoking, and infections. Our AI considers these factors in the prediction.';
    }
    
    // Accuracy
    if (lowerMessage.includes('accurate') || lowerMessage.includes('accuracy')) {
        return 'Our Random Forest models are trained on extensive medical datasets and validated using cross-validation. We also use SHAP (SHapley Additive exPlanations) to ensure interpretability and transparency in predictions.';
    }
    
    // Recommendations
    if (lowerMessage.includes('recommend') || lowerMessage.includes('advice')) {
        return 'Based on your risk level, you\'ll receive personalized recommendations including: prenatal care frequency, lifestyle modifications, monitoring protocols, and when to seek immediate medical attention.';
    }
    
    // Default response
    return 'I\'m here to help! You can ask me about preterm birth, fetal acidemia, EHG/CTG signals, risk factors, how to use the system, or general pregnancy health questions.';
}

// Welcome message on first load
if (chatbotMessages.children.length === 0) {
    addMessage('Hello! I\'m your medical assistant. How can I help you today?', 'bot');
}