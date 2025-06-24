document.addEventListener("DOMContentLoaded", function () {
  let currentBotColor = '';
  let currentBotIcon = '';

  const defaultBots = [
    { name: 'Physics Bot', color: 'emerald', icon: '⚡', description: 'Unravel the mysteries of the universe!', status: 'Offline' },
    { name: 'Machine Learning', color: 'amber', icon: '📈', description: 'Master equations with elegance!', status: 'Online' },
    
   
  ];

  let customBots = JSON.parse(localStorage.getItem('customBots')) || [];

  function renderBots() {
    const botGrid = document.getElementById('botGrid');
    if (!botGrid) {
      console.warn("botGrid not found.");
      return;
    }
    botGrid.innerHTML = '';
    const allBots = [...defaultBots, ...customBots];

    allBots.forEach((bot, index) => {
      const botCard = document.createElement('div');
      botCard.className = `bot-card bg-white rounded-xl p-8 text-center border border-gray-200 hover:border-${bot.color}-500 transition-all duration-300 cursor-pointer animate-fadeInUp`;
      botCard.style.animationDelay = `${0.1 * (index + 1)}s`;
      botCard.innerHTML = `
        <div class="flex justify-end mb-2">
          <span class="status-toggle text-xs font-medium ${bot.status === 'Online' ? 'text-green-600 bg-green-100' : 'text-gray-500 bg-gray-100'} rounded-full px-2 py-1 cursor-pointer hover:${bot.status === 'Online' ? 'text-green-800' : 'text-gray-800'}">${bot.status}</span>
        </div>
        <span class="emoji-icon text-${bot.color}-600 mb-4 block">${bot.icon}</span>
        <h3 class="text-xl font-semibold text-${bot.color}-600">${bot.name}</h3>
        <p class="text-sm text-gray-600 mt-2">${bot.description}</p>
        <a href="#" class="text-sm text-red-600 mt-3 block hover:underline" onclick="openChatModal('${bot.name}', '${bot.color}', '${bot.icon}')">Chat with me</a>
      `;
      botGrid.appendChild(botCard);
    });
  }

  window.openChatModal = function (botName, color, icon) {
    const modal = document.getElementById('chatModal');
    const botNameElement = document.getElementById('chatBotName');
    const botIconElement = document.getElementById('chatBotIcon');
    const chatHeader = document.getElementById('chatHeader');
    const chatBody = document.getElementById('chatBody');

    if (!modal || !botNameElement || !botIconElement || !chatHeader || !chatBody) {
      console.warn("Some chat modal elements are missing.");
      return;
    }

    botNameElement.textContent = botName;
    botIconElement.textContent = icon;
    currentBotColor = color;
    currentBotIcon = icon;

    botIconElement.className = `text-2xl mr-3 text-${color}-600`;
    botNameElement.className = `text-lg font-semibold text-${color}-600`;
    chatHeader.className = `flex items-center justify-between p-4 border-b border-${color}-200 bg-${color}-50`;

    chatBody.innerHTML = `
      <div class="chat-message self-start bg-gray-100 rounded-lg p-3">
        <p class="text-sm">Hello! I'm here to help you with your questions. What would you like to explore today?</p>
      </div>
    `;

    modal.classList.remove('hidden');
    document.getElementById('chatInput')?.focus();
  };

  window.closeChatModal = function () {
    const modal = document.getElementById('chatModal');
    if (modal) modal.classList.add('hidden');
  };

  window.sendMessage = function () {
    const input = document.getElementById('chatInput');
    const chatBody = document.getElementById('chatBody');
    const message = input?.value.trim();

    if (message && chatBody) {
      const userMessage = document.createElement('div');
      userMessage.className = 'chat-message self-end bg-indigo-100 rounded-lg p-3';
      userMessage.innerHTML = `<p class="text-sm">${message}</p>`;
      chatBody.appendChild(userMessage);

      setTimeout(() => {
        const botMessage = document.createElement('div');
        botMessage.className = 'chat-message self-start bg-gray-100 rounded-lg p-3';
        botMessage.innerHTML = `<p class="text-sm">That's a great question! Let me help you with that...</p>`;
        chatBody.appendChild(botMessage);
        chatBody.scrollTop = chatBody.scrollHeight;
      }, 500);

      input.value = '';
      chatBody.scrollTop = chatBody.scrollHeight;
    }
  };

  const chatInput = document.getElementById('chatInput');
  chatInput?.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') sendMessage();
  });

  window.openAddBotModal = function () {
    const modal = document.getElementById('addBotModal');
    modal?.classList.remove('hidden');
    document.getElementById('botName')?.focus();
  };

  window.closeAddBotModal = function () {
    const modal = document.getElementById('addBotModal');
    if (modal) modal.classList.add('hidden');
    document.getElementById('botName').value = '';
    document.getElementById('botDescription').value = '';
    document.getElementById('botIcon').value = '';
    document.getElementById('botColor').value = 'emerald';
  };

  window.addNewBot = function () {
    const botName = document.getElementById('botName')?.value.trim();
    const botDescription = document.getElementById('botDescription')?.value.trim();
    const botIcon = document.getElementById('botIcon')?.value.trim();
    const botColor = document.getElementById('botColor')?.value;

    if (botName && botDescription && botIcon && botColor) {
      const newBot = {
        name: botName,
        description: botDescription,
        icon: botIcon,
        color: botColor,
        status: 'Online'
      };

      customBots.push(newBot);
      localStorage.setItem('customBots', JSON.stringify(customBots));
      renderBots();
      closeAddBotModal();
    } else {
      alert('Please fill in all fields to add a new bot.');
    }
  };

  // Initial render
  renderBots();
});
