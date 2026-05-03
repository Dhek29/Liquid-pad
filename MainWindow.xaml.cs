using System.IO;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Effects;
using Microsoft.Win32;

namespace UsersFile
{
    public partial class MainWindow : Window
    {
        private string currentFilePath = string.Empty;
        private bool isTextChanged = false;
        private bool showLineNumbers = false;
        private double currentFontSize = 13;

        public MainWindow()
        {
            InitializeComponent();
            InitializeApp();
        }

        private void InitializeApp()
        {
            Editor.TextWrapping = TextWrapping.Wrap;
            UpdateDocumentStats();
            UpdateStatusBar("Ready");
            
            // Set default dark theme
            SetDarkTheme(null, null);
        }

        // ==================== THEME FUNCTIONS ====================
        
        private void SetDarkTheme(object sender, RoutedEventArgs e)
        {
            Editor.Background = new SolidColorBrush(Color.FromRgb(30, 30, 30));
            Editor.Foreground = new SolidColorBrush(Color.FromRgb(212, 212, 212));
            Editor.CaretBrush = Brushes.White;
            Editor.Effect = null;
            this.Background = new SolidColorBrush(Color.FromRgb(30, 30, 30));
            this.AllowsTransparency = false;
            this.WindowStyle = WindowStyle.SingleBorderWindow;
            UpdateStatusBar("Dark theme applied");
        }

        private void SetLightTheme(object sender, RoutedEventArgs e)
        {
            Editor.Background = new SolidColorBrush(Color.FromRgb(255, 255, 255));
            Editor.Foreground = new SolidColorBrush(Color.FromRgb(0, 0, 0));
            Editor.CaretBrush = Brushes.Black;
            Editor.Effect = null;
            this.Background = new SolidColorBrush(Color.FromRgb(240, 240, 240));
            this.AllowsTransparency = false;
            this.WindowStyle = WindowStyle.SingleBorderWindow;
            UpdateStatusBar("Light theme applied");
        }

        private void SetBlurTheme(object sender, RoutedEventArgs e)
        {
            // Make editor transparent with blur effect
            Editor.Background = Brushes.Transparent;
            Editor.Foreground = new SolidColorBrush(Color.FromRgb(255, 255, 255));
            Editor.CaretBrush = Brushes.White;
            Editor.Effect = new BlurEffect { Radius = 6 };
            
            // Make window transparent to see wallpaper
            this.Background = Brushes.Transparent;
            this.AllowsTransparency = true;
            this.WindowStyle = WindowStyle.None;
            
            UpdateStatusBar("✨ Blur theme applied - Your wallpaper is visible behind!");
        }

        // ==================== FILE OPERATIONS ====================
        
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
                var dialog = new OpenFileDialog 
                { 
                    Filter = "Text Files (*.txt)|*.txt|All Files (*.*)|*.*",
                    Title = "Open File"
                };
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
                        MessageBox.Show($"Error: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
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
            var dialog = new SaveFileDialog 
            { 
                Filter = "Text Files (*.txt)|*.txt", 
                FileName = "Untitled.txt",
                Title = "Save As"
            };
            if (dialog.ShowDialog() == true)
            {
                File.WriteAllText(dialog.FileName, Editor.Text, Encoding.UTF8);
                currentFilePath = dialog.FileName;
                isTextChanged = false;
                UpdateTitle();
                UpdateStatusBar("File saved!");
            }
        }

        private bool ConfirmSave()
        {
            if (!isTextChanged) return true;
            var result = MessageBox.Show("Save changes?", "Unsaved Changes", 
                                        MessageBoxButton.YesNoCancel, MessageBoxImage.Question);
            if (result == MessageBoxResult.Yes) SaveFile_Click(null, null);
            return result != MessageBoxResult.Cancel;
        }

        private void Exit_Click(object sender, RoutedEventArgs e)
        {
            if (ConfirmSave()) Close();
        }

        // ==================== EDIT OPERATIONS ====================
        
        private void Undo_Click(object sender, RoutedEventArgs e) => Editor.Undo();
        private void Redo_Click(object sender, RoutedEventArgs e) => Editor.Redo();
        private void Cut_Click(object sender, RoutedEventArgs e) => Editor.Cut();
        private void Copy_Click(object sender, RoutedEventArgs e) => Editor.Copy();
        private void Paste_Click(object sender, RoutedEventArgs e) => Editor.Paste();
        private void SelectAll_Click(object sender, RoutedEventArgs e) => Editor.SelectAll();

        // ==================== FORMAT OPERATIONS ====================
        
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
            UpdateStatusBar("Converted to UPPERCASE");
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
            UpdateStatusBar("Converted to lowercase");
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
            UpdateStatusBar("Capitalized each word");
        }

        // ==================== VIEW OPERATIONS ====================
        
        private void WordWrapToggle_Click(object sender, RoutedEventArgs e)
        {
            Editor.TextWrapping = WordWrapCheckbox.IsChecked == true ? TextWrapping.Wrap : TextWrapping.NoWrap;
            UpdateStatusBar($"Word wrap {(WordWrapCheckbox.IsChecked == true ? "enabled" : "disabled")}");
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
                LineNumbersColumn.Width = new GridLength(60);
            }
            else
            {
                LineNumbersColumn.Width = new GridLength(0);
            }
        }

        // ==================== SETTINGS ====================
        
        private void OpenSettings(object sender, RoutedEventArgs e)
        {
            var settings = new SettingsWindow(currentFontSize);
            if (settings.ShowDialog() == true)
            {
                currentFontSize = settings.FontSize;
                Editor.FontSize = currentFontSize;
                LineNumbers.FontSize = currentFontSize;
                UpdateStatusBar($"Font size changed to {currentFontSize}");
            }
        }

        // ==================== EDITOR EVENTS ====================
        
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

        private void Editor_PreviewKeyDown(object sender, KeyEventArgs e)
        {
            // Tab to spaces
            if (e.Key == Key.Tab)
            {
                e.Handled = true;
                Editor.SelectedText = "    ";
            }
            
            // Keyboard shortcuts
            if (Keyboard.Modifiers == ModifierKeys.Control)
            {
                switch (e.Key)
                {
                    case Key.S: SaveFile_Click(null, null); e.Handled = true; break;
                    case Key.O: OpenFile_Click(null, null); e.Handled = true; break;
                    case Key.N: NewFile_Click(null, null); e.Handled = true; break;
                    case Key.Z: Undo_Click(null, null); e.Handled = true; break;
                    case Key.Y: Redo_Click(null, null); e.Handled = true; break;
                    case Key.X: Cut_Click(null, null); e.Handled = true; break;
                    case Key.C: Copy_Click(null, null); e.Handled = true; break;
                    case Key.V: Paste_Click(null, null); e.Handled = true; break;
                    case Key.A: SelectAll_Click(null, null); e.Handled = true; break;
                }
            }
        }

        // ==================== UI UPDATES ====================
        
        private void UpdateTitle()
        {
            var name = string.IsNullOrEmpty(currentFilePath) ? "Untitled" : Path.GetFileName(currentFilePath);
            Title = $"{name}{(isTextChanged ? "*" : "")} - UsersFile";
            FileNameDisplay.Text = name;
            FileStatus.Text = isTextChanged ? "● Unsaved" : "● Saved";
            FileStatus.Foreground = isTextChanged ? new SolidColorBrush(Color.FromRgb(255, 184, 108)) : new SolidColorBrush(Color.FromRgb(78, 201, 176));
        }

        private void UpdateDocumentStats()
        {
            var text = Editor.Text;
            var wordCount = string.IsNullOrWhiteSpace(text) ? 0 : 
                text.Split(new[] { ' ', '\n', '\r', '\t' }, StringSplitOptions.RemoveEmptyEntries).Length;
            var charCount = text.Length;
            var lineCount = Editor.LineCount;
            
            StatsWords.Text = $"📝 Words: {wordCount:N0}";
            StatsChars.Text = $"📄 Characters: {charCount:N0}";
            StatsLines.Text = $"📏 Lines: {lineCount:N0}";
        }

        private void UpdateStatusBar(string message)
        {
            Dispatcher.Invoke(() =>
            {
                StatusText.Text = message;
                Task.Delay(3000).ContinueWith(_ => Dispatcher.Invoke(() =>
                {
                    if (StatusText.Text == message)
                        StatusText.Text = "Ready";
                }));
            });
        }
    }
}
