using System.Windows;

namespace UsersFile
{
    public partial class SettingsWindow : Window
    {
        public double FontSize { get; private set; }
        
        public SettingsWindow(double currentFontSize)
        {
            InitializeComponent();
            FontSizeSlider.Value = currentFontSize;
            FontSizeValue.Text = currentFontSize.ToString();
            
            FontSizeSlider.ValueChanged += (s, e) => 
            {
                FontSizeValue.Text = ((int)FontSizeSlider.Value).ToString();
            };
        }
        
        private void ApplyButton_Click(object sender, RoutedEventArgs e)
        {
            FontSize = FontSizeSlider.Value;
            DialogResult = true;
            Close();
        }
        
        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }
    }
}
