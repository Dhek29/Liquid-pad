using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
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
        private SmartAIAssistant aiAssistant;
        private double currentZoom = 1.0;
        private bool showLineNumbers = false;
        private FindReplaceWindow findReplaceWindow;

        public MainWindow()
        {
            InitializeComponent();
            InitializeApp();
        }

        private void InitializeApp()
        {
            // Initialize AI
            aiAssistant = new SmartAIAssistant();
            
            // Initialize settings
            SidebarColumn.Width = new GridLength(250);
            StatusBar.Visibility = Visibility.Visible;
            StatusBarCheckbox.IsChecked = true;
            WordWrapCheckbox.IsChecked = true;
            
            // Set default editor settings
            Editor.TextWrapping = TextWrapping.Wrap;
            
            // Update UI
            UpdateStatusBar("Ready");
            UpdateDocumentStats();
            
            // Setup keyboard shortcuts
            InitializeKeyboardShortcuts();
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
                        case Key.P: Print_Click(null, null); e.Handled = true; break;
                        case Key.Z: Undo_Click(null, null); e.Handled = true; break;
                        case Key.Y: Redo_Click(null, null); e.Handled = true; break;
                        case Key.X: Cut_Click(null, null); e.Handled = true; break;
                        case Key.C: Copy_Click(null, null); e.Handled = true; break;
                        case Key.V: Paste_Click(null, null); e.Handled = true; break;
                        case Key.A: SelectAll_Click(null, null); e.Handled = true; break;
                        case Key.F: Find_Click(null, null); e.Handled = true; break;
                        case Key.H: Replace_Click(null, null); e.Handled = true; break;
                        case Key.Add: ZoomIn_Click(null, null); e.Handled = true; break;
                        case Key.Subtract: ZoomOut_Click(null, null); e.Handled = true; break;
                        case Key.D0: ResetZoom_Click(null, null); e.Handled = true; break;
                    }
                }
                else if (e.Key == Key.F1)
                {
                    ShowHelp();
                    e.Handled = true;
                }
                else if (e.Key == Key.F4 && Keyboard.Modifiers == ModifierKeys.Alt)
                {
                    Exit_Click(null, null);
                    e.Handled = true;
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
                }
                UpdateStatusBar("Settings applied");
            }
        }

        private string GetCurrentTheme()
        {
            if (Editor.Background == Brushes.Black)
                return "Dark";
            else if (Editor.Background == Brushes.White)
                return "Light";
            else
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
                    this.Background = Brushes.Transparent;
                    this.AllowsTransparency = true;
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
                OpenFileDialog openFileDialog = new OpenFileDialog
                {
                    Filter = "Text Files (*.txt)|*.txt|Rich Text Format (*.rtf)|*.rtf|All Files (*.*)|*.*",
                    DefaultExt = ".txt"
                };

                if (openFileDialog.ShowDialog() == true)
                {
                    try
                    {
                        string content = File.ReadAllText(openFileDialog.FileName, Encoding.UTF8);
                        Editor.Text = content;
                        currentFilePath = openFileDialog.FileName;
                        UpdateTitle();
                        isTextChanged = false;
                        UpdateDocumentStats();
                        UpdateStatusBar($"Opened: {Path.GetFileName(currentFilePath)}");
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"Error opening file: {ex.Message}", "Error", 
                                      MessageBoxButton.OK, MessageBoxImage.Error);
                    }
                }
            }
        }

        private void SaveFile_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(currentFilePath))
            {
                SaveAs_Click(sender, e);
            }
            else
            {
                try
                {
                    File.WriteAllText(currentFilePath, Editor.Text, Encoding.UTF8);
                    isTextChanged = false;
                    UpdateTitle();
                    UpdateStatusBar("File saved successfully!");
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error saving file: {ex.Message}", "Error", 
                                  MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void SaveAs_Click(object sender, RoutedEventArgs e)
        {
            SaveFileDialog saveFileDialog = new SaveFileDialog
            {
                Filter = "Text Files (*.txt)|*.txt|All Files (*.*)|*.*",
                DefaultExt = ".txt",
                FileName = string.IsNullOrEmpty(currentFilePath) ? "Untitled.txt" : Path.GetFileName(currentFilePath)
            };

            if (saveFileDialog.ShowDialog() == true)
            {
                try
                {
                    File.WriteAllText(saveFileDialog.FileName, Editor.Text, Encoding.UTF8);
                    currentFilePath = saveFileDialog.FileName;
                    isTextChanged = false;
                    UpdateTitle();
                    UpdateStatusBar("File saved successfully!");
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error saving file: {ex.Message}", "Error", 
                                  MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void Print_Click(object sender, RoutedEventArgs e)
        {
            PrintDialog printDialog = new PrintDialog();
            if (printDialog.ShowDialog() == true)
            {
                // Simple print implementation
                var flowDocument = new FlowDocument(new Paragraph(new Run(Editor.Text)));
                printDialog.PrintDocument(((IDocumentPaginatorSource)flowDocument).DocumentPaginator, "UsersFile Print");
                UpdateStatusBar("Document sent to printer");
            }
        }

        private bool ConfirmSave()
        {
            if (isTextChanged)
            {
                var result = MessageBox.Show("Do you want to save changes?", "Unsaved Changes", 
                                           MessageBoxButton.YesNoCancel, MessageBoxImage.Question);
                if (result == MessageBoxResult.Yes)
                {
                    SaveFile_Click(null, null);
                    return !isTextChanged;
                }
                return result != MessageBoxResult.Cancel;
            }
            return true;
        }

        private void Exit_Click(object sender, RoutedEventArgs e)
        {
            if (ConfirmSave())
            {
                Close();
            }
        }

        // Edit Operations
        private void Undo_Click(object sender, RoutedEventArgs e)
        {
            if (Editor.CanUndo)
                Editor.Undo();
        }

        private void Redo_Click(object sender, RoutedEventArgs e)
        {
            if (Editor.CanRedo)
                Editor.Redo();
        }

        private void Cut_Click(object sender, RoutedEventArgs e)
        {
            Editor.Cut();
        }

        private void Copy_Click(object sender, RoutedEventArgs e)
        {
            Editor.Copy();
        }

        private void Paste_Click(object sender, RoutedEventArgs e)
        {
            Editor.Paste();
        }

        private void SelectAll_Click(object sender, RoutedEventArgs e)
        {
            Editor.SelectAll();
        }

        private void Find_Click(object sender, RoutedEventArgs e)
        {
            if (findReplaceWindow == null || !findReplaceWindow.IsVisible)
            {
                findReplaceWindow = new FindReplaceWindow(Editor);
                findReplaceWindow.Owner = this;
                findReplaceWindow.Show();
            }
            else
            {
                findReplaceWindow.Focus();
            }
        }

        private void Replace_Click(object sender, RoutedEventArgs e)
        {
            Find_Click(sender, e);
        }

        // View Operations
        private void WordWrapToggle_Click(object sender, RoutedEventArgs e)
        {
            Editor.TextWrapping = WordWrapCheckbox.IsChecked == true ? TextWrapping.Wrap : TextWrapping.NoWrap;
            UpdateStatusBar($"Word wrap {(WordWrapCheckbox.IsChecked == true ? "enabled" : "disabled")}");
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
                int lineCount = Editor.LineCount;
                StringBuilder lineNumbers = new StringBuilder();
                for (int i = 1; i <= lineCount; i++)
                {
                    lineNumbers.AppendLine(i.ToString());
                }
                LineNumbers.Text = lineNumbers.ToString();
                LineNumbersColumn.Width = new GridLength(50);
            }
            else
            {
                LineNumbersColumn.Width = new GridLength(0);
            }
        }

        private void ZoomIn_Click(object sender, RoutedEventArgs e)
        {
            currentZoom = Math.Min(currentZoom + 0.1, 3.0);
            ApplyZoom();
        }

        private void ZoomOut_Click(object sender, RoutedEventArgs e)
        {
            currentZoom = Math.Max(currentZoom - 0.1, 0.5);
            ApplyZoom();
        }

        private void ResetZoom_Click(object sender, RoutedEventArgs e)
        {
            currentZoom = 1.0;
            ApplyZoom();
        }

        private void ApplyZoom()
        {
            Editor.FontSize = 14 * currentZoom;
            ZoomLevel.Text = $"Zoom: {Math.Round(currentZoom * 100)}%";
        }

        // Format Operations
        private void ToUpper_Click(object sender, RoutedEventArgs e)
        {
            if (!string.IsNullOrEmpty(Editor.SelectedText))
            {
                int start = Editor.SelectionStart;
                int length = Editor.SelectionLength;
                Editor.Text = Editor.Text.Substring(0, start) + 
                             Editor.SelectedText.ToUpper() + 
                             Editor.Text.Substring(start + length);
                Editor.Select(start, length);
            }
            else
            {
                Editor.Text = Editor.Text.ToUpper();
            }
            UpdateStatusBar("Converted to UPPERCASE");
        }

        private void ToLower_Click(object sender, RoutedEventArgs e)
        {
            if (!string.IsNullOrEmpty(Editor.SelectedText))
            {
                int start = Editor.SelectionStart;
                int length = Editor.SelectionLength;
                Editor.Text = Editor.Text.Substring(0, start) + 
                             Editor.SelectedText.ToLower() + 
                             Editor.Text.Substring(start + length);
                Editor.Select(start, length);
            }
            else
            {
                Editor.Text = Editor.Text.ToLower();
            }
            UpdateStatusBar("Converted to lowercase");
        }

        private void Capitalize_Click(object sender, RoutedEventArgs e)
        {
            var text = Editor.SelectedText;
            if (string.IsNullOrEmpty(text))
                text = Editor.Text;

            var words = text.Split(' ');
            for (int i = 0; i < words.Length; i++)
            {
                if (words[i].Length > 0)
                {
                    words[i] = char.ToUpper(words[i][0]) + words[i].Substring(1).ToLower();
                }
            }
            
            string result = string.Join(" ", words);
            
            if (!string.IsNullOrEmpty(Editor.SelectedText))
            {
                int start = Editor.SelectionStart;
                int length = Editor.SelectionLength;
                Editor.Text = Editor.Text.Substring(0, start) + result + Editor.Text.Substring(start + length);
                Editor.Select(start, result.Length);
            }
            else
            {
                Editor.Text = result;
            }
            UpdateStatusBar("Capitalized each word");
        }

        private void RemoveExtraSpaces_Click(object sender, RoutedEventArgs e)
        {
            string text = Editor.Text;
            var cleaned = System.Text.RegularExpressions.Regex.Replace(text, @"\s+", " ");
            Editor.Text = cleaned;
            UpdateStatusBar("Removed extra spaces");
        }

        private void SortLines_Click(object sender, RoutedEventArgs e)
        {
            var lines = Editor.Text.Split(new[] { Environment.NewLine }, StringSplitOptions.None);
            Array.Sort(lines);
            Editor.Text = string.Join(Environment.NewLine, lines);
            UpdateStatusBar("Lines sorted alphabetically");
        }

        // AI Functions
        private void AiToggle_Checked(object sender, RoutedEventArgs e)
        {
            AIPanelColumn.Width = new GridLength(350);
            AIPanel.Visibility = Visibility.Visible;
            UpdateStatusBar("AI Assistant enabled - Ask me anything!");
        }

        private void AiToggle_Unchecked(object sender, RoutedEventArgs e)
        {
            AIPanelColumn.Width = new GridLength(0);
            AIPanel.Visibility = Visibility.Collapsed;
            UpdateStatusBar("AI Assistant disabled");
        }

        private void QuickAI_Click(object sender, RoutedEventArgs e)
        {
            if (!AiToggle.IsChecked.HasValue || !AiToggle.IsChecked.Value)
            {
                AiToggle.IsChecked = true;
            }
            AIQuestion.Focus();
        }

        private async void AskAI_Click(object sender, RoutedEventArgs e)
        {
            await ProcessAIRequest();
        }

        private async void AIQuestion_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Enter && (Keyboard.Modifiers == ModifierKeys.Control || Keyboard.Modifiers == ModifierKeys.Shift))
            {
                e.Handled = true;
                await ProcessAIRequest();
            }
        }

        private async Task ProcessAIRequest()
        {
            if (string.IsNullOrWhiteSpace(AIQuestion.Text))
            {
                AddAIMessage("Please enter a question.", true);
                return;
            }

            string question = AIQuestion.Text;
            AddAIMessage(question, false);
            AIQuestion.Clear();

            try
            {
                // Get context (selected text or whole document)
                string context = string.IsNullOrEmpty(Editor.SelectedText) ? Editor.Text : Editor.SelectedText;
                
                AddAIMessage("🤔 Thinking...", true);
                
                string response = await aiAssistant.ProcessRequest(question, context);
                
                // Remove "Thinking..." message and add actual response
                if (ChatHistory.Children.Count > 0 && ChatHistory.Children[ChatHistory.Children.Count - 1] is Border lastBorder)
                {
                    if ((lastBorder.Child as TextBlock)?.Text == "🤔 Thinking...")
                    {
                        ChatHistory.Children.RemoveAt(ChatHistory.Children.Count - 1);
                    }
                }
                
                AddAIMessage(response, true);
                UpdateStatusBar("AI responded");
                
                // Scroll to bottom
                ChatScrollViewer.ScrollToBottom();
            }
            catch (Exception ex)
            {
                AddAIMessage($"Error: {ex.Message}", true);
                UpdateStatusBar("AI error occurred");
            }
        }

        private void AddAIMessage(string message, bool isAI)
        {
            var border = new Border
            {
                CornerRadius = new CornerRadius(8),
                Margin = new Thickness(0, 5, 0, 5),
                Padding = new Thickness(10)
            };

            if (isAI)
            {
                border.Background = new SolidColorBrush(Color.FromRgb(227, 242, 253));
                border.HorizontalAlignment = HorizontalAlignment.Left;
                border.MaxWidth = 280;
            }
            else
            {
                border.Background = new SolidColorBrush(Color.FromRgb(224, 224, 224));
                border.HorizontalAlignment = HorizontalAlignment.Right;
                border.MaxWidth = 280;
            }

            var textBlock = new TextBlock
            {
                Text = message,
                TextWrapping = TextWrapping.Wrap,
                FontSize = 12,
                Foreground = Brushes.Black
            };

            // Make clickable if contains code or commands
            if (message.Contains("•") || message.Contains("Try:"))
            {
                textBlock.MouseLeftButtonDown += (s, e) =>
                {
                    string cmd = message.Split('\n')[0];
                    AIQuestion.Text = cmd;
                };
                textBlock.Cursor = Cursors.Hand;
                textBlock.ToolTip = "Click to use this command";
            }

            border.Child = textBlock;
            ChatHistory.Children.Add(border);
            
            // Auto-scroll
            ChatScrollViewer.ScrollToBottom();
        }

        private void ClearAIChat_Click(object sender, RoutedEventArgs e)
        {
            ChatHistory.Children.Clear();
            AddWelcomeMessage();
        }

        private void AddWelcomeMessage()
        {
            var border = new Border
            {
                Background = new SolidColorBrush(Color.FromRgb(227, 242, 253)),
                CornerRadius = new CornerRadius(8),
                Margin = new Thickness(0, 5, 0, 5),
                Padding = new Thickness(10)
            };
            
            var textBlock = new TextBlock
            {
                Text = "👋 Welcome! I'm your AI assistant. Ask me to:\n\n• 'Summarize this text'\n• 'Check grammar'\n• 'Improve my writing'\n• 'Translate to Spanish'\n• 'Make it formal/casual'\n• 'Generate bullet points'\n• 'Explain a concept'\n• 'Find keywords'\n• 'Check spelling'\n• 'Extract tasks'",
                TextWrapping = TextWrapping.Wrap,
                FontSize = 12,
                Foreground = Brushes.Black
            };
            
            border.Child = textBlock;
            ChatHistory.Children.Add(border);
        }

        private void ShowHelp()
        {
            MessageBox.Show(@"UsersFile Notepad - Help

Keyboard Shortcuts:
• Ctrl+N - New File     • Ctrl+O - Open File
• Ctrl+S - Save         • Ctrl+P - Print
• Ctrl+Z - Undo         • Ctrl+Y - Redo
• Ctrl+X - Cut          • Ctrl+C - Copy
• Ctrl+V - Paste        • Ctrl+A - Select All
• Ctrl+F - Find         • Ctrl+H - Replace
• Ctrl++ - Zoom In      • Ctrl+- - Zoom Out
• Ctrl+0 - Reset Zoom   • F1 - Help
• Alt+F4 - Exit

AI Commands:
• Summarize my text
• Check grammar
• Improve writing
• Translate to [language]
• Make it formal/casual
• Generate bullet points
• Explain [concept]
• Find keywords
• Extract tasks

Features:
• Word wrap, status bar, line numbers
• Multiple themes (Dark/Light/Blur)
• AI Assistant with smart responses
• Document statistics
• Print support", "UsersFile Help", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        // UI Updates
        private void Editor_TextChanged(object sender, TextChangedEventArgs e)
        {
            isTextChanged = true;
            UpdateTitle();
            UpdateDocumentStats();
            if (showLineNumbers)
                UpdateLineNumbers();
        }

        private void Editor_SelectionChanged(object sender, RoutedEventArgs e)
        {
            UpdateCursorPosition();
        }

        private void Editor_PreviewKeyDown(object sender, KeyEventArgs e)
        {
            // Handle Tab key for indentation
            if (e.Key == Key.Tab)
            {
                e.Handled = true;
                int start = Editor.SelectionStart;
                Editor.Text = Editor.Text.Insert(start, "    ");
                Editor.SelectionStart = start + 4;
            }
        }

        private void UpdateTitle()
        {
            string fileName = string.IsNullOrEmpty(currentFilePath) ? "Untitled" : Path.GetFileName(currentFilePath);
            string modified = isTextChanged ? "*" : "";
            this.Title = $"{fileName}{modified} - UsersFile Notepad";
            FileNameDisplay.Text = fileName + modified;
        }

        private void UpdateDocumentStats()
        {
            string text = Editor.Text;
            int charCount = text.Length;
            int wordCount = string.IsNullOrWhiteSpace(text) ? 0 : text.Split(new[] { ' ', '\n', '\r' }, StringSplitOptions.RemoveEmptyEntries).Length;
            int lineCount = Editor.LineCount;
            int paraCount = string.IsNullOrWhiteSpace(text) ? 0 : text.Split(new[] { Environment.NewLine + Environment.NewLine }, StringSplitOptions.RemoveEmptyEntries).Length;
            
            StatsWords.Text = $"Words: {wordCount}";
            StatsChars.Text = $"Characters: {charCount}";
            StatsLines.Text = $"Lines: {lineCount}";
            StatsParas.Text = $"Paragraphs: {paraCount}";
        }

        private void UpdateStatusBar(string message = null)
        {
            Dispatcher.Invoke(() =>
            {
                if (message != null)
                {
                    StatusText.Text = message;
                    var timer = new System.Timers.Timer(3000);
                    timer.Elapsed += (s, e) => Dispatcher.Invoke(() =>
                    {
                        if (StatusText.Text == message)
                            UpdateCursorPosition();
                    });
                    timer.AutoReset = false;
                    timer.Start();
                }
                else
                {
                    UpdateCursorPosition();
                }
            });
        }

        private void UpdateCursorPosition()
        {
            int line = Editor.GetLineIndexFromCharacterIndex(Editor.CaretIndex);
            int col = Editor.CaretIndex - Editor.GetCharacterIndexFromLineIndex(line);
            int selected = Editor.SelectionLength;
            
            if (selected > 0)
                CursorPosition.Text = $"Ln {line + 1}, Col {col + 1} | Sel {selected} chars";
            else
                CursorPosition.Text = $"Ln {line + 1}, Col {col + 1}";
        }
    }
}
