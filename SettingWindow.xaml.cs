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
            InitializeValues(currentFont, currentTheme, currentFontSize);
        }

        private void InitializeValues(string currentFont, string currentTheme, double currentFontSize)
        {
            // Set current theme
            switch (currentTheme)
            {
                case "Dark":
                    ThemeBox.SelectedIndex = 0;
                    break;
                case "Light":
                    ThemeBox.SelectedIndex = 1;
                    break;
                case "Blur":
                    ThemeBox.SelectedIndex = 2;
                    break;
                default:
                    ThemeBox.SelectedIndex = 0;
                    break;
            }

            // Set current font
            bool fontFound = false;
            for (int i = 0; i < FontBox.Items.Count; i++)
            {
                if ((FontBox.Items[i] as ComboBoxItem)?.Content.ToString() == currentFont)
                {
                    FontBox.SelectedIndex = i;
                    fontFound = true;
                    break;
                }
            }
            if (!fontFound)
                FontBox.SelectedIndex = 0;

            // Set current font size
            FontSizeSlider.Value = currentFontSize;
            FontSizeValue.Text = currentFontSize.ToString();

            // Hook up events
            FontBox.SelectionChanged += (s, e) => UpdatePreview();
            ThemeBox.SelectionChanged += (s, e) => UpdatePreview();
            FontSizeSlider.ValueChanged += (s, e) => 
            {
                FontSizeValue.Text = ((int)FontSizeSlider.Value).ToString();
                UpdatePreview();
            };

            UpdatePreview();
        }

        private void UpdatePreview()
        {
            var theme = ((ComboBoxItem)ThemeBox.SelectedItem)?.Content.ToString();
            var font = ((ComboBoxItem)FontBox.SelectedItem)?.Content.ToString();
            
            PreviewText.FontFamily = new FontFamily(font ?? "Calibri");
            PreviewText.FontSize = FontSizeSlider.Value;
            
            if (theme == "🌙 Dark")
            {
                PreviewText.Foreground = Brushes.White;
                (PreviewText.Parent as Border).Background = Brushes.Black;
            }
            else if (theme == "☀️ Light")
            {
                PreviewText.Foreground = Brushes.Black;
                (PreviewText.Parent as Border).Background = Brushes.White;
            }
            else
            {
                PreviewText.Foreground = Brushes.White;
                (PreviewText.Parent as Border).Background = Brushes.FromRgb(100, 100, 100);
            }
        }

        private void ApplySettings(object sender, RoutedEventArgs e)
        {
            if (ThemeBox.SelectedItem != null)
            {
                string theme = ((ComboBoxItem)ThemeBox.SelectedItem).Content.ToString();
                SelectedTheme = theme.Replace("🌙 ", "").Replace("☀️ ", "").Replace("✨ ", "");
            }
            else
            {
                SelectedTheme = "Dark";
            }

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
