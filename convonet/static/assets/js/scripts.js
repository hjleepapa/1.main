// Convonet Todo JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Convonet Todo system loaded');
    
    // Add any interactive functionality here
    const statusElement = document.querySelector('.status');
    if (statusElement) {
        statusElement.textContent = 'System Ready';
    }
});

// Function to test API endpoint
async function testAPI() {
    const testPrompt = "Create a test todo item";
    const response = await fetch('/convonet_todo/run_agent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: testPrompt })
    });
    
    const result = await response.json();
    console.log('API Test Result:', result);
    return result;
}
