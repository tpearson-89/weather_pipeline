resource "aws_glue_catalog_database" "weather_db" {
  name = "${var.project_name}_db"
}

resource "aws_s3_object" "glue_script" {
  bucket = aws_s3_bucket.clean_bucket.id
  key    = "scripts/glue_etl.py"
  source = "${path.module}/../src/glue_etl.py"
  etag   = filemd5("${path.module}/../src/glue_etl.py")
}

resource "aws_glue_job" "weather_etl" {
  name     = "${var.project_name}-etl-job"
  role_arn = aws_iam_role.glue_role.arn

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.clean_bucket.id}/scripts/glue_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--TempDir"                          = "s3://${aws_s3_bucket.clean_bucket.id}/temp/"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-metrics"                   = "true"
  }

  glue_version      = "5.0"
  number_of_workers = 2
  worker_type       = "G.1X"

  depends_on = [
    aws_s3_object.glue_script
  ]
}