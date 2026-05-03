using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace UsersFile.AI
{
    public class GeminiAIService
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiKey;
        
        public GeminiAIService(string apiKey)
        {
            _apiKey = apiKey;
            _httpClient = new HttpClient();
            _httpClient.Timeout = TimeSpan.FromSeconds(30);
        }
        
        public async Task<string> GetResponseAsync(string userMessage, string documentContext)
        {
            try
            {
                var url = $"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={_apiKey}";
                
                var prompt = string.IsNullOrEmpty(documentContext) 
                    ? userMessage 
                    : $"Document text: {documentContext.Substring(0, Math.Min(1500, documentContext.Length))}\n\nUser: {userMessage}\n\nAssistant:";
                
                var request = new
                {
                    contents = new[] { new { parts = new[] { new { text = prompt } } } }
                };
                
                var json = JsonSerializer.Serialize(request);
                var response = await _httpClient.PostAsync(url, new StringContent(json, Encoding.UTF8, "application/json"));
                var responseJson = await response.Content.ReadAsStringAsync();
                
                if (response.IsSuccessStatusCode)
                {
                    using var doc = JsonDocument.Parse(responseJson);
                    var text = doc.RootElement
                        .GetProperty("candidates")[0]
                        .GetProperty("content")
                        .GetProperty("parts")[0]
                        .GetProperty("text")
                        .GetString();
                    return text ?? "No response";
                }
                
                return $"API Error: {response.StatusCode}";
            }
            catch (Exception ex)
            {
                return $"Error: {ex.Message}";
            }
        }
    }
}
