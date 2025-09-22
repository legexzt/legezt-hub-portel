using UnityEngine;
using UnityEngine.SceneManagement;

public class ShadowRunner_Start : MonoBehaviour
{
    public void OnStartGame()
    {
        SceneManager.LoadScene("ShadowRunner_Level1");
    }

    public void OnBackButton()
    {
        SceneManager.LoadScene("GameLibrary");
    }
}