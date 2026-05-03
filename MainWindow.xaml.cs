using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Effects;
using Microsoft.Win32;
using UsersFile.AI;

namespace UsersFile
{
    public partial class MainWindow : Window
    {
        private bool isSidebarOpen = true;
        private string currentFilePath = string.Empty;
        private bool isTextChanged = false;
        private GeminiAIService? _geminiAI;
        private bool _aiEnabled = false;
        private double currentZoom = 14;
        private bool showLineNumbers = false;

        public MainWindow()
        {
            InitializeComponent();
            InitializeApp();
        }

        private void InitializeApp()
        {
            SidebarColumn.Width = new GridLength(250);
            StatusBar.Visibility = Visibility.Visible;
            
            // Initialize Gemini AI - REPLACE WITH YOUR API KEY
            string apiKey = "YOUR_GEMINI_API_KEY_HERE";
            
            if (!string.IsNullOrEmpty(apiKey) && apiKey != "YOUR_GEMINI_API_KEY_HERE")
            {
                try
                {
                    _geminiAI = new GeminiAIService(apiKey);
                    UpdateStatusBar("✅ Gemini AI Ready! Enable AI from sidebar.");
                }
                catch (Exception ex)
                {
                    UpdateStatusBar($"⚠️ AI Error: {ex.Message}");
                }
            }
            else
            {
                UpdateStatusBar("⚠️ Add your Gemini API key in MainWindow.xaml.cs");
            }
            
            InitializeKeyboardShortcuts();
            UpdateDocumentStats();
        }

        private void InitializeKeyboardShortcuts()
        {
            this.PreviewKeyDown += (s, e) =>
            {
                if (Keyboard.Modifiers == ModifierKeys.Control)
                {
                    switch (e.Key)
                    {
                        case Key.N: NewFile_Click(null, null); e.Handled = true; break;
                        case Key.O: OpenFile_Click(null, null); e.Handled = true; break;
                        case Key.S: SaveFile_Click(null, null); e.Handled = true; break;
                        case Key.Z: Undo_Click(null, null); e.Handled = true; break;
                        case Key.Y: Redo_Click(null, null); e.Handled = true; break;
                        case Key.X: Cut_Click(null, null); e.Handled = true; break;
                        case Key.C: Copy_Click(null, null); e.Handled = true; break;
                        case Key.V: Paste_Click(null, null); e.Handled = true; break;
                        case Key.A: SelectAll_Click(null, null); e.Handled = true; break;
                    }
                }
            };
        }

        private void ToggleSidebar(object sender, RoutedEventArgs e)
        {
            isSidebarOpen = !isSidebarOpen;
            SidebarColumn.Width = isSidebarOpen ? new GridLength(250) : new GridLength(0);
        }

        private void OpenSettings(object sender, RoutedEventArgs e)
        {
            var settings = new SettingsWindow(Editor.FontFamily.Source, GetCurrentTheme(), Editor.FontSize);
            if (settings.ShowDialog() == true)
            {
                ApplyTheme(settings.SelectedTheme);
                ApplyFont(settings.SelectedFont);
                if (settings.SelectedFontSize > 0)
                {
                    Editor.FontSize = settings.SelectedFontSize;
                    currentZoom = settings.SelectedFontSize;
                }
                UpdateStatusBar("Settings applied");
            }
        }

        private string GetCurrentTheme()
        {
            if (Editor.Background == Brushes.Black) return "Dark";
            if (Editor.Background == Brushes.White) return "Light";
            return "Blur";
        }

        private void ApplyTheme(string? theme)
        {
            switch (theme)
            {
                case "Dark":
                    Editor.Background = Brushes.Black;
                    Editor.Foreground = Brushes.White;
                    Editor.Effect = null;
                    LineNumbers.Background = Brushes.DarkGray;
                    LineNumbers.Foreground = Brushes.White;
                    break;
                case "Light":
                    Editor.Background = Brushes.White;
                    Editor.Foreground = Brushes.Black;
                    Editor.Effect = null;
                    LineNumbers.Background = Brushes.LightGray;
                    LineNumbers.Foreground = Brushes.Black;
                    break;
                case "Blur":
                    Editor.Background = Brushes.Transparent;
                    Editor.Foreground = Brushes.White;
                    Editor.Effect = new BlurEffect { Radius = 3 };
                    Background = Brushes.Transparent;
                    AllowsTransparency = true;
                    break;
            }
        }

        private void ApplyFont(string? font)
        {
            if (!string.IsNullOrEmpty(font))
            {
                Editor.FontFamily = new FontFamily(font);
                LineNumbers.FontFamily = new FontFamily(font);
            }
        }

        // File Operations
        private void NewFile_Click(object sender, RoutedEventArgs e)
        {
            if (ConfirmSave())
            {
                Editor.Clear();
                currentFilePath = string.Empty;
                UpdateTitle();
                UpdateDocumentStats();
                UpdateStatusBar("New file created");
            }
        }

        private void OpenFile_Click(object sender, RoutedEventArgs e)
        {
            if (ConfirmSave())
            {
                var dialog = new OpenFileDialog { Filter = "Text Files (*.txt)|*.txt|All Files (*.*)|*.*" };
                if (dialog.ShowDialog() == true)
                {
                    try
                    {
                        Editor.Text = File.ReadAllText(dialog.FileName, Encoding.UTF8);
                        currentFilePath = dialog.FileName;
                        isTextChanged = false;
                        UpdateTitle();
                        UpdateDocumentStats();
                        UpdateStatusBar($"Opened: {Path.GetFileName(currentFilePath)}");
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"Error: {ex.Message}", "Error");
                    }
                }
            }
        }

        private void SaveFile_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(currentFilePath))
                SaveAs_Click(sender, e);
            else
            {
                File.WriteAllText(currentFilePath, Editor.Text, Encoding.UTF8);
                isTextChanged = false;
                UpdateTitle();
                UpdateStatusBar("File saved!");
            }
        }

        private void SaveAs_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new SaveFileDialog { Filter = "Text Files (*.txt)|*.txt", FileName = "Untitled.txt" };
            if (dialog.ShowDialog() == true)
            {
                File.WriteAllText(dialog.FileName, Editor.Text, Encoding.UTF8);
                currentFilePath = dialog.FileName;
                isTextChanged = false;
                UpdateTitle();
                UpdateStatusBar("File saved!");
            }
        }

        private void Print_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new PrintDialog();
            if (dialog.ShowDialog() == true)
                UpdateStatusBar("Print sent");
        }

        private bool ConfirmSave()
        {
            if (!isTextChanged) return true;
            var result = MessageBox.Show("Save changes?", "Unsaved", MessageBoxButton.YesNoCancel);
            if (result == MessageBoxResult.Yes) SaveFile_Click(null, null);
            return result != MessageBoxResult.Cancel;
        }

        private void Exit_Click(object sender, RoutedEventArgs e)
        {
            if (ConfirmSave()) Close();
        }

        // Edit Operations
        private void Undo_Click(object sender, RoutedEventArgs e) => Editor.Undo();
        private void Redo_Click(object sender, RoutedEventArgs e) => Editor.Redo();
        private void Cut_Click(object sender, RoutedEventArgs e) => Editor.Cut();
        private void Copy_Click(object sender, RoutedEventArgs e) => Editor.Copy();
        private void Paste_Click(object sender, RoutedEventArgs e) => Editor.Paste();
        private void SelectAll_Click(object sender, RoutedEventArgs e) => Editor.SelectAll();

        // View Operations
        private void WordWrapToggle_Click(object sender, RoutedEventArgs e)
        {
            Editor.TextWrapping = WordWrapCheckbox.IsChecked == true ? TextWrapping.Wrap : TextWrapping.NoWrap;
        }

        private void StatusBarToggle_Click(object sender, RoutedEventArgs e)
        {
            StatusBar.Visibility = StatusBarCheckbox.IsChecked == true ? Visibility.Visible : Visibility.Collapsed;
        }

        private void LineNumbersToggle_Click(object sender, RoutedEventArgs e)
        {
            showLineNumbers = LineNumbersCheckbox.IsChecked == true;
            UpdateLineNumbers();
        }

        private void UpdateLineNumbers()
        {
            if (showLineNumbers)
            {
                var lines = new StringBuilder();
                for (int i = 1; i <= Editor.LineCount; i++) lines.AppendLine(i.ToString());
                LineNumbers.Text = lines.ToString();
                LineNumbersColumn.Width = new GridLength(50);
            }
            else
            {
                LineNumbersColumn.Width = new GridLength(0);
            }
        }

        private void ZoomIn_Click(object sender, RoutedEventArgs e)
        {
            currentZoom = Math.Min(currentZoom + 2, 72);
            Editor.FontSize = currentZoom;
        }

        private void ZoomOut_Click(object sender, RoutedEventArgs e)
        {
            currentZoom = Math.Max(currentZoom - 2, 8);
            Editor.FontSize = currentZoom;
        }

        private void ResetZoom_Click(object sender, RoutedEventArgs e)
        {
            currentZoom = 14;
            Editor.FontSize = currentZoom;
        }

        // Format Operations
        private void ToUpper_Click(object sender, RoutedEventArgs e)
        {
            if (!string.IsNullOrEmpty(Editor.SelectedText))
            {
                var start = Editor.SelectionStart;
                var length = Editor.SelectionLength;
                Editor.Text = Editor.Text.Substring(0, start) + Editor.SelectedText.ToUpper() + Editor.Text.Substring(start + length);
                Editor.Select(start, length);
            }
            else Editor.Text = Editor.Text.ToUpper();
        }

        private void ToLower_Click(object sender, RoutedEventArgs e)
        {
            if (!string.IsNullOrEmpty(Editor.SelectedText))
            {
                var start = Editor.SelectionStart;
                var length = Editor.SelectionLength;
                Editor.Text = Editor.Text.Substring(0, start) + Editor.SelectedText.ToLower() + Editor.Text.Substring(start + length);
                Editor.Select(start, length);
            }
            else Editor.Text = Editor.Text.ToLower();
        }

        private void Capitalize_Click(object sender, RoutedEventArgs e)
        {
            var text = string.IsNullOrEmpty(Editor.SelectedText) ? Editor.Text : Editor.SelectedText;
            var words = text.Split(' ');
            for (int i = 0; i < words.Length; i++)
                if (words[i].Length > 0)
                    words[i] = char.ToUpper(words[i][0]) + words[i].Substring(1).ToLower();
            var result = string.Join(" ", words);
            
            if (!string.IsNullOrEmpty(Editor.SelectedText))
            {
                var start = Editor.SelectionStart;
                var length = Editor.SelectionLength;
                Editor.Text = Editor.Text.Substring(0, start) + result + Editor.Text.Substring(start + length);
                Editor.Select(start, result.Length);
            }
            else Editor.Text = result;
        }

        private void RemoveExtraSpaces_Click(object sender, RoutedEventArgs e)
        {
            Editor.Text = System.Text.RegularExpressions.Regex.Replace(Editor.Text, @"\s+", " ");
        }

        private void SortLines_Click(object sender, RoutedEventArgs e)
        {
            var lines = Editor.Text.Split(new[] { Environment.NewLine }, StringSplitOptions.None);
            Array.Sort(lines);
            Editor.Text = string.Join(Environment.NewLine, lines);
        }

        // AI Functions
        private void AiToggle_Checked(object sender, RoutedEventArgs e)
        {
            _aiEnabled = true;
            AIPanelColumn.Width = new GridLength(350);
            AIPanel.Visibility = Visibility.Visible;
            UpdateStatusBar("🤖 AI Enabled - Ask me anything!");
        }

        private void AiToggle_Unchecked(object sender, RoutedEventArgs e)
        {
            _aiEnabled = false;
            AIPanelColumn.Width = new GridLength(0);
            AIPanel.Visibility = Visibility.Collapsed;
            UpdateStatusBar("AI Disabled");
        }

        private void QuickAI_Click(object sender, RoutedEventArgs e)
        {
            if (AiToggle.IsChecked != true) AiToggle.IsChecked = true;
            AIQuestion.Focus();
        }

        private async void AskAI_Click(object sender, RoutedEventArgs e)
        {
            await ProcessAIRequest();
        }

        private async void AIQuestion_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Enter && Keyboard.Modifiers == ModifierKeys.Control)
            {
                e.Handled = true;
                await ProcessAIRequest();
            }
        }

        private async Task ProcessAIRequest()
        {
            if (!_aiEnabled || _geminiAI == null)
            {
                AddAIMessage("⚠️ Please enable AI Assistant from the sidebar first!", true);
                return;
            }

            if (string.IsNullOrWhiteSpace(AIQuestion.Text))
            {
                AddAIMessage("Please enter a question.", true);
                return;
            }

            var question = AIQuestion.Text;
            AddAIMessage(question, false);
            AIQuestion.Clear();

            try
            {
                AddAIMessage("🤔 Thinking...", true);
                var context = string.IsNullOrEmpty(Editor.SelectedText) ? Editor.Text : Editor.SelectedText;
                var response = await _geminiAI.GetResponseAsync(question, context);
                
                if (ChatHistory.Children.Count > 0 && ChatHistory.Children[^1] is Border lastBorder &&
                    (lastBorder.Child as TextBlock)?.Text == "🤔 Thinking...")
                    ChatHistory.Children.RemoveAt(ChatHistory.Children.Count - 1);
                
                AddAIMessage(response, true);
                UpdateStatusBar("✅ AI responded");
                ChatScrollViewer.ScrollToBottom();
            }
            catch (Exception ex)
            {
                AddAIMessage($"❌ Error: {ex.Message}", true);
                UpdateStatusBar("AI error occurred");
            }
        }

        private void AddAIMessage(string message, bool isAI)
        {
            var border = new Border
            {
                CornerRadius = new CornerRadius(8),
                Margin = new Thickness(0, 5, 0, 5),
                Padding = new Thickness(10),
                Background = isAI ? new SolidColorBrush(Color.FromRgb(227, 242, 253)) : new SolidColorBrush(Color.FromRgb(224, 224, 224)),
                HorizontalAlignment = isAI ? HorizontalAlignment.Left : HorizontalAlignment.Right,
                MaxWidth = 280
            };
            
            border.Child = new TextBlock { Text = message, TextWrapping = TextWrapping.Wrap, FontSize = 12 };
            ChatHistory.Children.Add(border);
            ChatScrollViewer.ScrollToBottom();
        }

        private void ClearAIChat_Click(object sender, RoutedEventArgs e)
        {
            ChatHistory.Children.Clear();
            AddAIMessage("👋 Chat cleared! Ask me anything about your text.", true);
        }

        // UI Updates
        private void Editor_TextChanged(object sender, TextChangedEventArgs e)
        {
            isTextChanged = true;
            UpdateTitle();
            UpdateDocumentStats();
            if (showLineNumbers) UpdateLineNumbers();
        }

        private void Editor_SelectionChanged(object sender, RoutedEventArgs e)
        {
            var line = Editor.GetLineIndexFromCharacterIndex(Editor.CaretIndex);
            var col = Editor.CaretIndex - Editor.GetCharacterIndexFromLineIndex(line);
            CursorPosition.Text = $"Ln {line + 1}, Col {col + 1}";
        }

        private void UpdateTitle()
        {
            var name = string.IsNullOrEmpty(currentFilePath) ? "Untitled" : Path.GetFileName(currentFilePath);
            Title = $"{name}{(isTextChanged ? "*" : "")} - UsersFile";
            FileNameDisplay.Text = name + (isTextChanged ? "*" : "");
        }

        private void UpdateDocumentStats()
        {
            var text = Editor.Text;
            var words = string.IsNullOrWhiteSpace(text) ? 0 : text.Split(new[] { ' ', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries).Length;
            StatsWords.Text = $"Words: {words}";
            StatsChars.Text = $"Characters: {text.Length}";
            StatsLines.Text = $"Lines: {Editor.LineCount}";
        }

        private void UpdateStatusBar(string message)
        {
            Dispatcher.Invoke(() =>
            {
                StatusText.Text = message;
                Task.Delay(3000).ContinueWith(_ => Dispatcher.Invoke(() =>
                {
                    if (StatusText.Text == message)
                    {
                        var line = Editor.GetLineIndexFromCharacterIndex(Editor.CaretIndex);
                        var col = Editor.CaretIndex - Editor.GetCharacterIndexFromLineIndex(line);
                        StatusText.Text = "Ready";
                        CursorPosition.Text = $"Ln {line + 1}, Col {col + 1}";
                    }
                }));
            });
        }
    }
}
