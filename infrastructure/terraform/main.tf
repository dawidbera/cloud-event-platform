# SQS Queue for Dead Letter Events
resource "aws_sqs_queue" "dlq" {
  name                      = "cep-dlq-${var.environment}"
  message_retention_seconds = 86400
}

# S3 Bucket for archiving old events / reports
resource "aws_s3_bucket" "archive" {
  bucket = "cep-archive-${var.environment}"
}

resource "aws_s3_bucket_ownership_controls" "archive_ownership" {
  bucket = aws_s3_bucket.archive.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "archive_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.archive_ownership]

  bucket = aws_s3_bucket.archive.id
  acl    = "private"
}
