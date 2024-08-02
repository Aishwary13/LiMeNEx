# Load the gene count matrix CSV file into a data frame
gene_count_matrix <- read.csv("scRNAseq_expression_matrix.csv", row.names = 1)

# Convert the row names (gene symbols) to a column for processing
gene_count_matrix$GeneSymbol <- rownames(gene_count_matrix)

# Remove duplicate rows based on the GeneSymbol column
gene_count_matrix_unique <- gene_count_matrix %>%
  distinct(GeneSymbol, .keep_all = TRUE)

# Set the row names back to GeneSymbol and remove the GeneSymbol column
rownames(gene_count_matrix_unique) <- gene_count_matrix_unique$GeneSymbol
gene_count_matrix_unique$GeneSymbol <- NULL

# Save the cleaned data frame back to a CSV file
write.csv(gene_count_matrix_unique, "gene_count_matrix_unique.csv", row.names = TRUE)