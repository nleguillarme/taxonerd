library(reticulate)

Sys.setenv(TOKENIZERS_PARALLELISM="false")
taxonerd <- NULL

.onLoad <- function(libname, pkgname) {
  envname = "r-taxonerd"
  if (!reticulate::virtualenv_exists(envname = "r-taxonerd")) {
    reticulate::virtualenv_create(envname)
  }
}

#' Install the TaxoNERD python package.
#'
#' @param version The package version. Default is the last release.
#' @param cuda.version Your CUDA version. Default = NULL.
#' @example \dontrun{install.taxonerd()}
#' @example \dontrun{install.taxonerd(version="1.3.3", cuda.version="cuda112")}
#' @export install.taxonerd
#' @import reticulate
install.taxonerd <- function(version="1.3.3", cuda.version=NULL) {
  # create a new environment 
  extras = ""
  if (!is.null(cuda.version)) {
    extras = paste("[",cuda.version,"]",sep="")
  }
  #reticulate::py_install(paste("taxonerd",extras,"==",version,sep=""), pip=TRUE)
  reticulate::virtualenv_install("r-taxonerd", packages = paste("taxonerd",extras,"==",version,sep=""), ignore_installed = TRUE)
  #taxonerd <- import.taxonerd()
  #print(taxonerd$`__version__`)
}

#' Import the TaxoNERD python package.
#'
#' @example import.taxonerd()
#' @import reticulate
import.taxonerd <- function() {
  use_virtualenv("r-taxonerd", required = TRUE)
  import("taxonerd")
}

#' Install the taxonomic entity recognition models.
#'
#' @param model The name of the model.
#' @param version The version of the model.
#' @example \dontrun{install.model("en_ner_eco_md", "1.3.0")}
#' @export install.model
#' @import reticulate
install.model <- function(model, version="1.3.0") {
  url = sprintf("https://github.com/nleguillarme/taxonerd/releases/download/v%s/%s-1.0.0.tar.gz", version, model)
  virtualenv_install("r-taxonerd", packages = url, ignore_installed = TRUE)
  #reticulate::py_install(url, envname="r-taxonerd", pip=TRUE)
}

#' Initialize the taxonomic entity recognition engine.
#'
#' @param model The name of the model. Default is en_ner_eco_md.
#' @param abbrev Set to TRUE to enable abbreviation detection. Default is FALSE.
#' @param sent Set to TRUE to enable sentence segmentation. Default is FALSE.
#' @param link The name of the entity linker. Default is NULL.
#' @param thresh The mention-entity candidate similarity threshold for entity linking. Default is 0.7.
#' @param gpu Set to TRUE to use GPU if available. Default is FALSE.
#' @return a TaxoNERD object.
#' @examples
#' \dontrun{init.taxonerd("en_ner_eco_md", TRUE)}
#' \dontrun{init.taxonerd("en_ner_eco_biobert", FALSE, TRUE, "taxref", 0.7, TRUE, FALSE)}
#' @export init.taxonerd
init.taxonerd <- function(model = "en_ner_eco_md", abbrev=FALSE, sent=FALSE, link=NULL, thresh=0.7, gpu=FALSE) {
  taxonerd <- import.taxonerd()
  return(taxonerd$TaxoNERD(model, abbrev, link, sent, thresh, gpu, FALSE))
}

#' Find taxonomic entity mentions in a piece of text.
#'
#' @param ner A TaxoNERD object.
#' @param text.string A string containing the text to be searched.
#' @return A data frame.
#' @examples
#' \dontrun{df = find.in.text(ner, "Brown bears (Ursus arctos) are recognised as opportunistic omnivores")}
#' @export find.in.text
find.in.text <- function(ner, text.string) {
  return(ner$find_in_text(text.string))
}

#' Find taxonomic entity mentions in file.
#'
#' @param ner A TaxoNERD object.
#' @param file.path The path to the file.
#' @param output.dir.path A path to a directory to store the results. Default is NULL.
#' @return A data frame if output.dir.path is NULL, the path to the file containing the results otherwise.
#' @examples
#' \dontrun{df = find.in.file(ner, "./my_corpus/my_file_1.txt")}
#' @export find.in.file
find.in.file <- function(ner, file.path, output.dir.path=NULL) {
  return(ner$find_in_file(file.path, output.dir.path))
}

#' Find taxonomic entity mentions in a corpus.
#'
#' @param ner A TaxoNERD object.
#' @param input.dir.path The path to the directory containing the corpus.
#' @param output.dir.path A path to a directory to store the results. Default is NULL.
#' @return A list of data frames if output.dir.path is NULL, a list of paths otherwise.
#' @examples
#' \dontrun{dfs = find.in.corpus(ner, "./my_corpus")}
#' @export find.in.corpus
find.in.corpus <- function(ner, input.dir.path, output.dir.path=NULL) {
  return(ner$find_in_corpus(input.dir.path, output.dir.path))
}