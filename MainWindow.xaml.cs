using System.IO;
using System.Text;
using System.Windows;
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

        public MainWindow()
        {
            InitializeComponent();
            InitializeApp();
        }

        private void InitializeApp()
        {
            UpdateStatus("Ready");
            UpdateDocumentStats();
            UpdateCursorPosition();
            Editor.Focus();
            DarkThemeRadio.IsChecked = true;
        }

        // ==================== THEME FUNCTIONS ====================
        
        private void DarkTheme_Checked(object sender, RoutedEventArgs e)
        {
            try
            {
                Editor.Background = new SolidColorBrush(Color.FromRgb(30, 30, 46));
                Editor.Foreground = new SolidColorBrush(Color.FromRgb(224, 224, 224));
                Editor.CaretBrush = Brushes.White;
                Editor.Effect = null;
                this.Background = new SolidColorBrush(Color.FromRgb(30, 30, 46));
                this.AllowsTransparency = false;
                this.WindowStyle = WindowStyle.SingleBorderWindow;
                UpdateStatus("Dark mode applied");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error: {ex.Message}");
            }
        }

        private void LightTheme_Checked(object sender, RoutedEventArgs e)
        {
            try
            {
                Editor.Background = new SolidColorBrush(Color.FromRgb(255, 255, 255));
                Editor.Foreground = new SolidColorBrush(Color.FromRgb(0, 0, 0));
                Editor.CaretBrush = Brushes.Black;
                Editor.Effect = null;
                this.Background = new SolidColorBrush(Color.FromRgb(240, 240, 245));
                this.AllowsTransparency = false;
                this.WindowStyle = WindowStyle.SingleBorderWindow;
                UpdateStatus("Light mode applied");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error: {ex.Message}");
            }
        }

        private void BlurTheme_Checked(object sender, RoutedEventArgs e)
        {
            try
            {
                Editor.Background = Brushes.Transparent;
                Editor.Foreground = new SolidColorBrush(Color.FromRgb(255, 255, 255));
                Editor.CaretBrush = Brushes.White;
                Editor.Effect = new BlurEffect { Radius = 8 };
                
                this.Background = Brushes.Transparent;
                this.AllowsTransparency = true;
                this.WindowStyle = WindowStyle.None;
                
                // Add border to make window visible
                this.BorderThickness = new Thickness(1);
                this.BorderBrush = new SolidColorBrush(Color.FromArgb(100, 255, 255, 255));
                
                UpdateStatus("✨ Blur mode - Your wallpaper is visible!");
            }
            catch (Exception ex)
            {
                UpdateStatus($"Error: {ex.Message}");
                // Fallback to dark mode
                DarkTheme_Checked(sender, e);
            }
        }

        // ==================== FILE OPERATIONS ====================
        
        private void NewFile_Click(object sender, RoutedEventArgs e)
        {
            if (ConfirmSave())
            {
                Editor.Clear();
                currentFilePath = string.Empty;
                isTextChanged = false;
                UpdateTitle();
                UpdateDocumentStats();
                UpdateStatus("New file created");
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
                        UpdateStatus($"Opened: {Path.GetFileName(currentFilePath)}");
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
                try
                {
                    File.WriteAllText(currentFilePath, Editor.Text, Encoding.UTF8);
                    isTextChanged = false;
                    UpdateTitle();
                    UpdateStatus("File saved!");
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
        }

        private void SaveAs_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new SaveFileDialog { Filter = "Text Files (*.txt)|*.txt", FileName = "Untitled.txt" };
            if (dialog.ShowDialog() == true)
            {
                try
                {
                    File.WriteAllText(dialog.FileName, Editor.Text, Encoding.UTF8);
                    currentFilePath = dialog.FileName;
                    isTextChanged = false;
                    UpdateTitle();
                    UpdateStatus("File saved!");
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
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
        
        private void Undo_Click(object sender, RoutedEventArgs e) 
        { 
            if (Editor.CanUndo) 
            {
                Editor.Undo();
                UpdateStatus("Undo");
            }
        }
        
        private void Redo_Click(object sender, RoutedEventArgs e) 
        { 
            if (Editor.CanRedo) 
            {
                Editor.Redo();
                UpdateStatus("Redo");
            }
        }
        
        private void Cut_Click(object sender, RoutedEventArgs e) 
        { 
            Editor.Cut();
            UpdateStatus("Cut");
        }
        
        private void Copy_Click(object sender, RoutedEventArgs e) 
        { 
            Editor.Copy();
            UpdateStatus("Copied");
        }
        
        private void Paste_Click(object sender, RoutedEventArgs e) 
        { 
            Editor.Paste();
            UpdateStatus("Pasted");
        }

        // ==================== FORMAT OPERATIONS ====================
        
        private void ToUpper_Click(object sender, RoutedEventArgs e)
        {
            if (Editor.SelectionLength > 0)
            {
                int start = Editor.SelectionStart;
                int length = Editor.SelectionLength;
                Editor.Text = Editor.Text.Substring(0, start) + Editor.SelectedText.ToUpper() + Editor.Text.Substring(start + length);
                Editor.Select(start, length);
            }
            else
            {
                Editor.Text = Editor.Text.ToUpper();
            }
            UpdateStatus("Converted to UPPERCASE");
        }

        private void ToLower_Click(object sender, RoutedEventArgs e)
        {
            if (Editor.SelectionLength > 0)
            {
                int start = Editor.SelectionStart;
                int length = Editor.SelectionLength;
                Editor.Text = Editor.Text.Substring(0, start) + Editor.SelectedText.ToLower() + Editor.Text.Substring(start + length);
                Editor.Select(start, length);
            }
            else
            {
                Editor.Text = Editor.Text.ToLower();
            }
            UpdateStatus("Converted to lowercase");
        }

        // ==================== SEARCH ====================
        
        private void Find_Click(object sender, RoutedEventArgs e)
        {
            string searchText = Microsoft.VisualBasic.Interaction.InputBox("Enter text to search:", "Find", "", -1, -1);
            if (!string.IsNullOrEmpty(searchText))
            {
                int index = Editor.Text.IndexOf(searchText, Editor.SelectionStart + Editor.SelectionLength, StringComparison.OrdinalIgnoreCase);
                if (index == -1 && Editor.SelectionStart > 0)
                    index = Editor.Text.IndexOf(searchText, 0, StringComparison.OrdinalIgnoreCase);
                
                if (index != -1)
                {
                    Editor.Select(index, searchText.Length);
                    Editor.Focus();
                    UpdateStatus($"Found: '{searchText}'");
                }
                else
                {
                    MessageBox.Show($"'{searchText}' not found.", "Find", MessageBoxButton.OK, MessageBoxImage.Information);
                }
            }
        }

        // ==================== SETTINGS ====================
        
        private void OpenSettings(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("Settings:\n\n• Font size coming soon\n• Auto-save coming soon\n• More features in next update", 
                          "Settings", MessageBoxButton.OK, MessageBoxImage.Information);
        }

        // ==================== UI EVENTS ====================
        
        private void Editor_TextChanged(object sender, System.Windows.Controls.TextChangedEventArgs e)
        {
            isTextChanged = true;
            UpdateTitle();
            UpdateDocumentStats();
        }

        private void Editor_SelectionChanged(object sender, RoutedEventArgs e)
        {
            UpdateCursorPosition();
        }

        private void Editor_PreviewKeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Tab)
            {
                e.Handled = true;
                Editor.SelectedText = "    ";
            }
            
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
                    case Key.F: Find_Click(null, null); e.Handled = true; break;
                }
            }
        }

        // ==================== UI UPDATES ====================
        
        private void UpdateTitle()
        {
            string name = string.IsNullOrEmpty(currentFilePath) ? "Untitled" : Path.GetFileName(currentFilePath);
            Title = $"{name}{(isTextChanged ? "*" : "")} - UsersFile";
            FileNameText.Text = name;
            ModifiedIndicator.Visibility = isTextChanged ? Visibility.Visible : Visibility.Collapsed;
        }

        private void UpdateDocumentStats()
        {
            string text = Editor.Text;
            int words = string.IsNullOrWhiteSpace(text) ? 0 : 
                text.Split(new[] { ' ', '\n', '\r', '\t' }, StringSplitOptions.RemoveEmptyEntries).Length;
            int chars = text.Length;
            int lines = Editor.LineCount;
            
            StatsWords.Text = $"📝 Words: {words:N0}";
            StatsChars.Text = $"📄 Characters: {chars:N0}";
            StatsLines.Text = $"📏 Lines: {lines:N0}";
        }

        private void UpdateCursorPosition()
        {
            try
            {
                int line = Editor.GetLineIndexFromCharacterIndex(Editor.CaretIndex);
                int col = Editor.CaretIndex - Editor.GetCharacterIndexFromLineIndex(line);
                CursorText.Text = $"Ln {line + 1}, Col {col + 1}";
            }
            catch { CursorText.Text = "Ln 1, Col 1"; }
        }

        private void UpdateStatus(string message)
        {
            StatusText.Text = message;
            var timer = new System.Timers.Timer(2000);
            timer.Elapsed += (s, ev) => Dispatcher.Invoke(() =>
            {
                if (StatusText.Text == message)
                    StatusText.Text = "Ready";
                timer.Stop();
                timer.Dispose();
            });
            timer.AutoReset = false;
            timer.Start();
        }
    }
}
