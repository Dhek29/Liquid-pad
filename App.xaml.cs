using System.Windows;

namespace UsersFile
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
            
            DispatcherUnhandledException += (s, args) =>
            {
                MessageBox.Show($"Error: {args.Exception.Message}", "Error", 
                              MessageBoxButton.OK, MessageBoxImage.Warning);
                args.Handled = true;
            };
        }
    }
}
