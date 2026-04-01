# setup_dvs.R — Install and configure dvs for PMX Benchmarks
#
# Run this script if you have benchmark data files > 100 MB.
# Smaller files are handled automatically by git-lfs — you do not need dvs.
#
# Usage:
#   Rscript scripts/setup_dvs.R

options(repos = c(
  a2ai = "https://a2-ai.r-universe.dev",
  CRAN = "https://cloud.r-project.org"
))

if (!requireNamespace("dvs", quietly = TRUE)) {
  message("Installing dvs...")
  install.packages("dvs")
}

library(dvs)

message("
dvs is installed. Common commands:

  dvs::dvs_add('benchmarks/<name>/data/train.csv')
    Register a file for dvs tracking (run once per file).

  dvs::dvs_push()
    Upload tracked files to blob storage.

  dvs::dvs_pull()
    Download tracked files from blob storage after cloning.

Before using dvs, edit dvs.yaml to set the correct backend, bucket, and
credentials. Contact the repository maintainers for access credentials.
")
