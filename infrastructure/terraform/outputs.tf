output "dlq_url" {
  description = "The URL of the Dead Letter Queue"
  value       = aws_sqs_queue.dlq.url
}

output "archive_bucket_name" {
  description = "The name of the S3 archive bucket"
  value       = aws_s3_bucket.archive.id
}
