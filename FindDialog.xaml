using System.Windows;
using System.Windows.Controls;

namespace UsersFile
{
    public partial class FindDialog : Window
    {
        private TextBox _targetEditor;
        
        public FindDialog(TextBox editor)
        {
            InitializeComponent();
            _targetEditor = editor;
            FindTextBox.Focus();
        }
        
        private void FindNext_Click(object sender, RoutedEventArgs e)
        {
            var findText = FindTextBox.Text;
            if (string.IsNullOrEmpty(findText)) return;
            
            var start = _targetEditor.SelectionStart + _targetEditor.SelectionLength;
            var index = _targetEditor.Text.IndexOf(findText, start, StringComparison.OrdinalIgnoreCase);
            
            if (index == -1 && start > 0)
                index = _targetEditor.Text.IndexOf(findText, 0, StringComparison.OrdinalIgnoreCase);
            
            if (index != -1)
            {
                _targetEditor.Select(index, findText.Length);
                _targetEditor.Focus();
            }
            else
            {
                MessageBox.Show($"'{findText}' not found.", "Find");
            }
        }
        
        private void FindTextBox_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            if (e.Key == System.Windows.Input.Key.Enter)
                FindNext_Click(sender, null);
        }
    }
}
