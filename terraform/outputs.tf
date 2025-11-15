output "raw_bucket_name" {
  value = aws_s3_bucket.raw_bucket.bucket
}

output "clean_bucket_name" {
  value = aws_s3_bucket.clean_bucket.bucket
}