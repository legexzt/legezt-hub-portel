using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class GameManager : MonoBehaviour
{
    public static GameManager instance;

    public Text scoreText;
    public Text timerText;
    public GameObject pauseMenu;
    public GameObject gameOverMenu;

    private int score = 0;
    private float timer = 0f;
    private bool isPaused = false;
    private bool isGameOver = false;

    void Awake()
    {
        instance = this;
    }

    void Update()
    {
        if (!isPaused && !isGameOver)
        {
            timer += Time.deltaTime;
            timerText.text = "Time: " + timer.ToString("F2");
        }

        if (Input.GetKeyDown(KeyCode.Escape))
        {
            TogglePause();
        }
    }

    public void AddScore(int points)
    {
        score += points;
        scoreText.text = "Score: " + score;
    }

    public void GameOver()
    {
        isGameOver = true;
        gameOverMenu.SetActive(true);
        Time.timeScale = 0;
    }

    public void TogglePause()
    {
        isPaused = !isPaused;
        pauseMenu.SetActive(isPaused);
        Time.timeScale = isPaused ? 0 : 1;
    }

    public void Restart()
    {
        Time.timeScale = 1;
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }

    public void ExitToMenu()
    {
        Time.timeScale = 1;
        SceneManager.LoadScene("GameLibrary");
    }

    public void NextLevel()
    {
        // Load next level scene
        int currentLevel = SceneManager.GetActiveScene().buildIndex;
        SceneManager.LoadScene(currentLevel + 1);
    }
}