using UnityEngine;

public class NanoBotController : MonoBehaviour
{
    public float speed = 5f;
    public GameObject bulletPrefab;

    void Update()
    {
        Move();
        if (Input.GetKeyDown(KeyCode.Space))
        {
            Shoot();
        }
    }

    void Move()
    {
        float moveX = Input.GetAxis("Horizontal");
        float moveY = Input.GetAxis("Vertical");
        Vector3 move = new Vector3(moveX, moveY, 0);
        transform.Translate(move * speed * Time.deltaTime);
    }

    void Shoot()
    {
        Instantiate(bulletPrefab, transform.position, Quaternion.identity);
    }
}