using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace UsersFile.AI
{
    public class SimpleAI
    {
        private readonly HttpClient httpClient;
        private const string API_URL = "https://api.openai.com/v1/chat/completions";
        
        // Note: You'll need to add your OpenAI API key
        // For testing without API key, this provides a mock response
        private readonly bool useMockAI = true;

        public SimpleAI()
        {
            httpClient = new HttpClient();
        }

        public async Task<string> GetAIResponse(string question)
        {
            if (useMockAI)
            {
                return GetMockAIResponse(question);
            }

            try
            {
                var requestBody = new
                {
                    model = "gpt-3.5-turbo",
                    messages = new[]
                    {
                        new { role = "user", content = question }
                    },
                    max_tokens = 500,
                    temperature = 0.7
                };

                var json = JsonSerializer.Serialize(requestBody);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                
                // Add your API key here when ready
                // httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer YOUR_API_KEY");
                
                var response = await httpClient.PostAsync(API_URL, content);
                var responseString = await response.Content.ReadAsStringAsync();
                
                if (response.IsSuccessStatusCode)
                {
                    var result = JsonSerializer.Deserialize<JsonElement>(responseString);
                    return result.GetProperty("choices")[0].GetProperty("message").GetProperty("content").GetString();
                }
                
                return $"API Error: {response.StatusCode}";
            }
            catch (Exception ex)
            {
                return $"Error: {ex.Message}";
            }
        }

        private string GetMockAIResponse(string question)
        {
            question = question.ToLower();
            
            if (question.Contains("help") || question.Contains("what can you do"))
            {
                return "I can help you with:\n• Writing and editing text\n• Grammar suggestions\n• Summarizing content\n• Answering questions about your text\n• Generating ideas\n\nJust ask me anything about your notepad content!";
            }
            else if (question.Contains("summar") && question.Contains("text"))
            {
                return "To summarize your text, please highlight the text you want me to summarize, or I can provide general tips on summarizing:\n1. Read the text carefully\n2. Identify key points\n3. Remove redundant information\n4. Write concisely\n\nWould you like me to help with a specific text?";
            }
            else if (question.Contains("grammar") || question.Contains("correct"))
            {
                return "I can help with grammar! Here are common issues to check:\n• Subject-verb agreement\n• Proper punctuation\n• Sentence structure\n• Word choice\n\nIf you share specific text, I can provide more detailed suggestions.";
            }
            else
            {
                return $"I understand you're asking about: {question}\n\nAs an AI assistant in this notepad, I can help with:\n• Text editing suggestions\n• Grammar correction\n• Content summarization\n• Writing improvements\n\nWhat specific help do you need with your text?";
            }
        }
    }
}
