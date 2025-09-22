using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenu : MonoBehaviour
{
    // UI Buttons assigned in Inspector
    public void OnPlayButton()
    {
        // Load Game Library Scene
        SceneManager.LoadScene("GameLibrary");
    }

    public void OnSettingsButton()
    {
        // Load Settings Scene
        SceneManager.LoadScene("Settings");
    }

    public void OnLoginButton()
    {
        // Load Login Scene
        SceneManager.LoadScene("Login");
    }

    public void OnExitButton()
    {
        // Quit application
        Application.Quit();
    }
}