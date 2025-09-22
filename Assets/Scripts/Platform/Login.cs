using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class Login : MonoBehaviour
{
    public InputField usernameField;
    public InputField passwordField;

    public void OnGuestLogin()
    {
        // Set guest mode
        PlayerPrefs.SetString("UserType", "Guest");
        SceneManager.LoadScene("MainMenu");
    }

    public void OnUserLogin()
    {
        // Simple check, in real app use authentication
        if (!string.IsNullOrEmpty(usernameField.text) && !string.IsNullOrEmpty(passwordField.text))
        {
            PlayerPrefs.SetString("UserType", "User");
            PlayerPrefs.SetString("Username", usernameField.text);
            SceneManager.LoadScene("MainMenu");
        }
        else
        {
            Debug.Log("Invalid credentials");
        }
    }

    public void OnBackButton()
    {
        SceneManager.LoadScene("MainMenu");
    }
}