using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace UsersFile
{
    public partial class SettingsWindow : Window
    {
        public string? SelectedTheme { get; private set; }
        public string? SelectedFont { get; private set; }
        public double SelectedFontSize { get; private set; }

        public SettingsWindow(string currentFont, string currentTheme, double currentFontSize)
        {
            InitializeComponent();
            
            ThemeBox.SelectedIndex = currentTheme == "Dark" ? 0 : currentTheme == "Light" ? 1 : 2;
            
            for (int i = 0; i < FontBox.Items.Count; i++)
                if (((ComboBoxItem)FontBox.Items[i]).Content.ToString() == currentFont)
                    FontBox.SelectedIndex = i;
            
            FontSizeSlider.Value = currentFontSize;
            FontSizeValue.Text = currentFontSize.ToString();
            
            FontSizeSlider.ValueChanged += (s, e) => FontSizeValue.Text = ((int)FontSizeSlider.Value).ToString();
        }

        private void ApplySettings(object sender, RoutedEventArgs e)
        {
            SelectedTheme = ((ComboBoxItem)ThemeBox.SelectedItem)?.Content.ToString() ?? "Dark";
            SelectedFont = ((ComboBoxItem)FontBox.SelectedItem)?.Content.ToString() ?? "Consolas";
            SelectedFontSize = FontSizeSlider.Value;
            DialogResult = true;
            Close();
        }

        private void Cancel_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }
    }
}
