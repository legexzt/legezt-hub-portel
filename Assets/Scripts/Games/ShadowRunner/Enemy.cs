using UnityEngine;

public class Enemy : MonoBehaviour
{
    public float speed = 5f;
    public Transform player;

    void Update()
    {
        if (player != null)
        {
            Vector3 direction = (player.position - transform.position).normalized;
            transform.Translate(direction * speed * Time.deltaTime);
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("Player"))
        {
            GameManager.instance.GameOver();
        }
    }
}