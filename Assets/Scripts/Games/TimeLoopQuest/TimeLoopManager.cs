using UnityEngine;
using UnityEngine.SceneManagement;

public class TimeLoopManager : MonoBehaviour
{
    public float loopTime = 60f;
    private float timer = 0f;

    void Update()
    {
        timer += Time.deltaTime;
        if (timer >= loopTime)
        {
            ResetLoop();
        }
    }

    void ResetLoop()
    {
        timer = 0f;
        // Save player knowledge or something
        // Reset scene
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }
}