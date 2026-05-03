using System.Windows;
using System.Windows.Controls;

namespace UsersFile
{
    public partial class FindReplaceWindow : Window
    {
        private TextBox targetEditor;
        private int lastSearchPosition = 0;
        
        public FindReplaceWindow(TextBox editor)
        {
            InitializeComponent();
            targetEditor = editor;
            FindTextBox.Focus();
        }
        
        private void FindNext_Click(object sender, RoutedEventArgs e)
        {
            PerformFind();
        }
        
        private void Replace_Click(object sender, RoutedEventArgs e)
        {
            if (PerformFind())
            {
                int start = targetEditor.SelectionStart;
                int length = targetEditor.SelectionLength;
                targetEditor.Text = targetEditor.Text.Substring(0, start) + 
                                   ReplaceTextBox.Text + 
                                   targetEditor.Text.Substring(start + length);
                targetEditor.SelectionStart = start;
                targetEditor.SelectionLength = ReplaceTextBox.Text.Length;
                lastSearchPosition = start + ReplaceTextBox.Text.Length;
            }
        }
        
        private void ReplaceAll_Click(object sender, RoutedEventArgs e)
        {
            string findText = FindTextBox.Text;
            string replaceText = ReplaceTextBox.Text;
            
            if (string.IsNullOrEmpty(findText))
                return;
            
            string text = targetEditor.Text;
            var options = System.Text.RegularExpressions.RegexOptions.None;
            
            if (!MatchCaseCheckbox.IsChecked == true)
                options |= System.Text.RegularExpressions.RegexOptions.IgnoreCase;
            
            if (MatchWholeWordCheckbox.IsChecked == true)
                findText = @"\b" + System.Text.RegularExpressions.Regex.Escape(findText) + @"\b";
            
            string newText = System.Text.RegularExpressions.Regex.Replace(text, findText, replaceText, options);
            targetEditor.Text = newText;
            
            MessageBox.Show($"Replaced all occurrences.", "Replace All", 
                          MessageBoxButton.OK, MessageBoxImage.Information);
        }
        
        private bool PerformFind()
        {
            string findText = FindTextBox.Text;
            if (string.IsNullOrEmpty(findText))
                return false;
            
            string text = targetEditor.Text;
            var options = System.StringComparison.OrdinalIgnoreCase;
            
            if (MatchCaseCheckbox.IsChecked == true)
                options = System.StringComparison.Ordinal;
            
            int startIndex = targetEditor.SelectionStart + targetEditor.SelectionLength;
            if (startIndex >= text.Length)
                startIndex = 0;
            
            int index = text.IndexOf(findText, startIndex, options);
            
            if (index == -1 && startIndex > 0)
            {
                index = text.IndexOf(findText, 0, options);
            }
            
            if (index != -1)
            {
                if (MatchWholeWordCheckbox.IsChecked == true)
                {
                    // Check if it's a whole word
                    if ((index == 0 || !char.IsLetterOrDigit(text[index - 1])) &&
                        (index + findText.Length >= text.Length || !char.IsLetterOrDigit(text[index + findText.Length])))
                    {
                        targetEditor.Select(index, findText.Length);
                        targetEditor.Focus();
                        lastSearchPosition = index + findText.Length;
                        return true;
                    }
                    else
                    {
                        // Not a whole word, continue searching
                        lastSearchPosition = index + 1;
                        return PerformFind();
                    }
                }
                else
                {
                    targetEditor.Select(index, findText.Length);
                    targetEditor.Focus();
                    lastSearchPosition = index + findText.Length;
                    return true;
                }
            }
            
            MessageBox.Show($"'{findText}' not found.", "Find", 
                          MessageBoxButton.OK, MessageBoxImage.Information);
            return false;
        }
        
        private void FindTextBox_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            if (e.Key == System.Windows.Input.Key.Enter)
            {
                PerformFind();
                e.Handled = true;
            }
        }
    }
}
