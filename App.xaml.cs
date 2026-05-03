using System.Windows;

namespace UsersFile
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
            
            // Set global exception handling
            DispatcherUnhandledException += (s, args) =>
            {
                MessageBox.Show($"Unexpected error: {args.Exception.Message}\n\nApp will continue running.", 
                              "Error", MessageBoxButton.OK, MessageBoxImage.Warning);
                args.Handled = true;
            };
        }
    }
}
