using UnityEngine;

public class PlayerController : MonoBehaviour
{
    public float moveSpeed = 10f;
    public float jumpForce = 5f;
    public float wallRunSpeed = 15f;
    public float wallRunTime = 2f;
    public LayerMask wallLayer;

    private Rigidbody rb;
    private bool isWallRunning = false;
    private float wallRunTimer = 0f;
    private Vector3 wallNormal;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }

    void Update()
    {
        Move();
        Jump();
        WallRun();
    }

    void Move()
    {
        float moveX = Input.GetAxis("Horizontal");
        float moveZ = Input.GetAxis("Vertical");

        Vector3 move = transform.right * moveX + transform.forward * moveZ;
        rb.MovePosition(rb.position + move * moveSpeed * Time.deltaTime);
    }

    void Jump()
    {
        if (Input.GetKeyDown(KeyCode.Space) && IsGrounded())
        {
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        }
    }

    void WallRun()
    {
        if (Physics.Raycast(transform.position, transform.forward, out RaycastHit hit, 1f, wallLayer))
        {
            if (!isWallRunning)
            {
                isWallRunning = true;
                wallRunTimer = wallRunTime;
                wallNormal = hit.normal;
                rb.useGravity = false;
            }
        }
        else
        {
            isWallRunning = false;
            rb.useGravity = true;
        }

        if (isWallRunning)
        {
            wallRunTimer -= Time.deltaTime;
            if (wallRunTimer <= 0)
            {
                isWallRunning = false;
                rb.useGravity = true;
            }
            else
            {
                rb.velocity = Vector3.up * wallRunSpeed;
            }
        }
    }

    bool IsGrounded()
    {
        return Physics.Raycast(transform.position, Vector3.down, 1.1f);
    }
}