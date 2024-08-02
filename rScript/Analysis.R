
# Load libraries
library(Seurat)
library(ggplot2)
library(dplyr)
library(svglite)
library(ggridges)
library(pheatmap)
library(ggrepel)
library(reshape2)
library(grid)
library(tibble)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
  stop("No session folder path provided.")
}
session_folder <- args[1]
base_path <- "D:/Raylab/NewNetwork"
session_path <- file.path(base_path,session_folder)

setwd(session_path)

dir.create(file.path(session_path,"plots"), recursive = TRUE, showWarnings = FALSE)

############################################################################################
# lines <- readLines("scRNAseq_expression_matrix.csv", n = 10)
# print(lines)

# # Step 2: Read the CSV file without automatically setting row names
# data <- read.csv("scRNAseq_expression_matrix.csv", header = TRUE, row.names = NULL)

# # Step 3: Inspect the first column for duplicates
# if (any(duplicated(data[, 1]))) {
#   cat("Duplicates found in the first column\n")
# } else {
#   cat("No duplicates in the first column\n")
# }

# # Step 4: Manually set unique row names if duplicates are found
# if (any(duplicated(data[, 1]))) {
#   data <- read.csv("scRNAseq_expression_matrix.csv", header = TRUE)
#   row.names(data) <- make.unique(as.character(data[, 1]))
#   data <- data[, -1]  # Remove the first column as it is now set as row names
# }


##############################################################################################
cat("here")
# Data Loading
arranged_data3 <- read.csv("scRNAseq_expression_matrix.csv",sep = ",",header = TRUE ,row.names = NULL)
# row.names(arranged_data3) <- make.unique(row.names(arranged_data3))
# names <- make.unique(as.character(arranged_data3$Gene))
arranged_data3 <- arranged_data3[!duplicated(arranged_data3$Gene), ]
# rownames(arranged_data3) <- names
rownames(arranged_data3) <- arranged_data3$Gene
arranged_data3 <- arranged_data3[,-1]

cat("here 1")

metadata <- read.csv("metadata.csv", row.names = 1)

cat("here 2")

# Data Preparation
normal_cols <- grep("Normal", names(arranged_data3), value = TRUE)
diseased_cols <- grep("Disease", names(arranged_data3), value = TRUE)
normal_data <- arranged_data3[, normal_cols, drop = FALSE]
diseased_data <- arranged_data3[, diseased_cols, drop = FALSE]
num_normal_samples <- length(normal_cols)
num_diseased_samples <- length(diseased_cols)
arranged_data <- arranged_data3[, c(normal_cols, diseased_cols)]
metadata <- data.frame(row.names = colnames(arranged_data), condition = c(rep("Normal", num_normal_samples), rep("Diseased", num_diseased_samples)))


# Create Seurat Object
gene_ids <- rownames(arranged_data3)
seurat_obj <- CreateSeuratObject(counts = arranged_data3, meta.data = metadata)

print(seurat_obj)

print(seurat_obj@meta.data)

# Quality Control and Normalization
seurat_obj[["percent.mt"]] <- PercentageFeatureSet(seurat_obj, pattern = "^MT-")

tryCatch({
  png("plots/violin_plot.png", width = 1200, height = 800)
  VlnPlot(seurat_obj, features = c("nFeature_RNA", "nCount_RNA", "percent.mt"), ncol = 3)
  dev.off()
}, error = function(e) { cat("Error in creating violin_plot.png: ", e$message, "\n") })

png("plots/violin_plot_by_condition.png", width = 1200, height = 800)
VlnPlot(seurat_obj, features = c("nFeature_RNA", "nCount_RNA", "percent.mt"), group.by = "condition", ncol = 3) + 
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
dev.off()

png("plots/feature_scatter.png", width = 800, height = 800)
FeatureScatter(seurat_obj, feature1 = "nCount_RNA", feature2 = "nFeature_RNA")
dev.off()

seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj)
top10 <- head(VariableFeatures(seurat_obj), 10)
plot1 <- VariableFeaturePlot(seurat_obj)
plot2 <- LabelPoints(plot = plot1, points = top10, repel = TRUE, xnudge = 0, ynudge = 0, max.overlaps = 100)

# Save Plot 4: Variable Feature Plot
png("plots/variable_feature_plot.png", width = 800, height = 800)
print(plot1)
dev.off()

# Save Plot 5: Labeled Variable Feature Plot
png("plots/labeled_variable_feature_plot.png", width = 800, height = 800)
print(plot2)
dev.off()


# Scaling of the Data
seurat_obj <- ScaleData(seurat_obj)

# Run PCA
seurat_obj <- RunPCA(seurat_obj, features = VariableFeatures(object = seurat_obj))

# Plot the elbow plot to visualize the variance explained by each PC
ElbowPlot(seurat_obj)

# Extract PCA feature loadings
loadings <- seurat_obj[["pca"]]@feature.loadings

# Convert the loadings to a data frame
loadings_df <- as.data.frame(loadings)
loadings_df$gene <- rownames(loadings_df)

# Function to create a plot for a given PC
create_pc_plot <- function(pc_num) {
  pc <- paste0("PC_", pc_num)
  top_genes <- loadings_df %>% arrange(desc(abs(get(pc)))) %>% head(10)
  top_genes$PC <- pc
  
  # Melt the data frame for ggplot
  loadings_melted <- melt(top_genes, id.vars = c("gene", "PC"))
  
  # Plot the feature loadings
  plot <- ggplot(loadings_melted, aes(x = gene, y = value, fill = variable)) +
    geom_bar(stat = "identity", position = "dodge") +
    theme_minimal(base_size = 15) +
    theme(
      panel.background = element_rect(fill = "white"),
      plot.background = element_rect(fill = "white"),
      axis.text.x = element_text(angle = 90, hjust = 1, size = 8)
    ) +
    labs(title = paste("Top 10 Genes for", pc), x = "Genes", y = "Loading Value")
  
  return(plot)
}

# Generate and save plots for each PC
for (i in 1:10) {
  plot <- create_pc_plot(i)
  ggsave(filename = paste0("plots/PC_", i, "_top_10_genes.png"), plot = plot, width = 10, height = 6, dpi = 300)
  svglite(filename = paste0("plots/PC_", i, "_top_10_genes.svg"), width = 10, height = 6)
  print(plot)
  dev.off()  # Close the SVG device
}

# Perform clustering on the Seurat object
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:10)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)

##Run UMAP on clusters
seurat_obj <- RunUMAP(seurat_obj, dims = 1:10)
umap_plot <- DimPlot(seurat_obj, reduction = "umap", group.by = "seurat_clusters")
print(umap_plot)
ggsave(filename = "plots/umap_plot.png", plot = umap_plot, width = 10, height = 6, dpi = 300)
svglite(filename = "plots/umap_plot.svg", width = 10, height = 6)
print(umap_plot)
dev.off() 

#Define function to perform differential expression analysis on clusters
perform_DE_analysis_within_cluster <- function(seurat_obj, cluster) {
  cluster_cells <- subset(seurat_obj, idents = cluster)
  markers <- FindMarkers(cluster_cells, ident.1 = "Diseased", ident.2 = "Normal", group.by = "condition")
  return(markers)
}
# Perform differential expression analysis for each cluster
clusters <- levels(seurat_obj$seurat_clusters)
cluster_markers <- list()


for (cluster in clusters) {
  cluster_markers[[cluster]] <- perform_DE_analysis_within_cluster(seurat_obj, cluster)
}

# Inspect the distribution of p_val and avg_log2FC
# for (cluster in names(cluster_markers)) {
#   cat("Cluster:", cluster, "\n")
#   cat("Summary of p_val:\n")
#   print(summary(cluster_markers[[cluster]]$p_val))
#   cat("Summary of avg_log2FC:\n")
#   print(summary(cluster_markers[[cluster]]$avg_log2FC))
# }

# Load lipid genes
lipid_genes <- read.csv("D:/Raylab/NewNetwork/rScript/lipid_genes.csv", header = TRUE, stringsAsFactors = FALSE)
lipid_gene_symbols <- lipid_genes[[1]]


# Cutoff values
cutoff_p_val <- 0.05  # p-value cutoff
cutoff_log2FC <- 0.1  # log2 fold change cutoff

# Initialize lists to store upregulated and downregulated lipid genes for each cluster
upregulated_lipid_genes <- list()
downregulated_lipid_genes <- list()
# print(cluster_markers)

# Process each cluster's significant markers
for (cluster in names(cluster_markers)) {
  # cat("Processing cluster:", cluster, "\n")
  significant_markers <- cluster_markers[[cluster]]
  
  # Check if the significant_markers data frame is not empty
  if (nrow(significant_markers) > 0) {
    # Apply cutoff values
    filtered_markers <- significant_markers %>% filter(p_val <= cutoff_p_val & abs(avg_log2FC) >= cutoff_log2FC)
    
    if (nrow(filtered_markers) > 0) {
      # Convert row names to a column named 'gene'
      filtered_markers <- filtered_markers %>% rownames_to_column(var = "gene")
      
      # Identify lipid genes
      lipid_genes_in_cluster <- filtered_markers %>% filter(gene %in% lipid_gene_symbols)
      # Separate upregulated and downregulated lipid genes
      upregulated_lipid_genes[[cluster]] <- lipid_genes_in_cluster %>% filter(avg_log2FC > 0) %>% pull(gene)
      downregulated_lipid_genes[[cluster]] <- lipid_genes_in_cluster %>% filter(avg_log2FC < 0) %>% pull(gene)
    
      # print(downregulated_lipid_genes[[cluster]])
    } else {
      # If no markers pass the cutoff, assign an empty vector
      upregulated_lipid_genes[[cluster]] <- character(0)
      downregulated_lipid_genes[[cluster]] <- character(0)
    }
  } else {
    # If no significant markers, assign an empty vector
    upregulated_lipid_genes[[cluster]] <- character(0)
    downregulated_lipid_genes[[cluster]] <- character(0)
  }
}

# Check the class of the lists
# cat("Class of upregulated_lipid_genes:", class(upregulated_lipid_genes), "\n")
# cat("Class of downregulated_lipid_genes:", class(downregulated_lipid_genes), "\n")


# Unlist the genes into a single vector
all_genes <- unlist(upregulated_lipid_genes)
# Create a data frame with one column
genes_df <- data.frame(genes = all_genes)
# Write the data frame to a CSV file
write.csv(genes_df, "upregulated_lipid_genes.csv", row.names = FALSE)

# Unlist the genes into a single vector
all_genes <- unlist(downregulated_lipid_genes)
# Create a data frame with one column
genes_df <- data.frame(genes = all_genes)
# Write the data frame to a CSV file
write.csv(genes_df, "downregulated_lipid_genes.csv", row.names = FALSE)

# Convert lists of character vectors to data frames for plotting
upregulated_data <- lapply(names(upregulated_lipid_genes), function(cluster) {
  if (length(upregulated_lipid_genes[[cluster]]) > 0) {
    data.frame(gene = upregulated_lipid_genes[[cluster]], 
               avg_log2FC = cluster_markers[[cluster]] %>% 
                 filter(row.names(cluster_markers[[cluster]]) %in% upregulated_lipid_genes[[cluster]]) %>% 
                 pull(avg_log2FC))
  } else {
    data.frame(gene = character(), avg_log2FC = numeric())
  }
})

downregulated_data <- lapply(names(downregulated_lipid_genes), function(cluster) {
  if (length(downregulated_lipid_genes[[cluster]]) > 0) {
    data.frame(gene = downregulated_lipid_genes[[cluster]], 
               avg_log2FC = cluster_markers[[cluster]] %>% 
                 filter(row.names(cluster_markers[[cluster]]) %in% downregulated_lipid_genes[[cluster]]) %>% 
                 pull(avg_log2FC))
  } else {
    data.frame(gene = character(), avg_log2FC = numeric())
  }
})


# Name the list elements
names(upregulated_data) <- names(upregulated_lipid_genes)
names(downregulated_data) <- names(downregulated_lipid_genes)



# Create and save bar plots of upregulated and downregulated lipid genes for each cluster in increasing order of log2FC value
for (cluster in names(upregulated_data)) {
  if (nrow(upregulated_data[[cluster]]) > 0) {
    upregulated_data[[cluster]] <- upregulated_data[[cluster]] %>% arrange(avg_log2FC)
    upregulated_plot <- ggplot(upregulated_data[[cluster]], aes(x = avg_log2FC, y = reorder(gene, avg_log2FC))) +
      geom_bar(stat = "identity", fill = "red") +
      theme_minimal() +
      theme(panel.background = element_rect(fill = "white", colour = "white"),
            plot.background = element_rect(fill = "white", colour = "white"),
            axis.text.x = element_text(angle = 90, hjust = 1, size = 8)) +
      labs(title = paste("Upregulated Lipid Genes in Cluster", cluster), x = "Log2 Fold Change", y = "Gene")
    ggsave(paste0("plots/upregulated_lipid_genes_cluster_", cluster, ".png"), plot = upregulated_plot, width = 10, height = 6)
    ggsave(paste0("plots/upregulated_lipid_genes_cluster_", cluster, ".svg"), plot = upregulated_plot, width = 10, height = 6)
    print(upregulated_plot)
  }
}

for (cluster in names(downregulated_data)) {
  if (nrow(downregulated_data[[cluster]]) > 0) {
    downregulated_data[[cluster]] <- downregulated_data[[cluster]] %>% arrange(avg_log2FC)
    downregulated_plot <- ggplot(downregulated_data[[cluster]], aes(x = avg_log2FC, y = reorder(gene, avg_log2FC))) +
      geom_bar(stat = "identity", fill = "blue") +
      theme_minimal() +
      theme(panel.background = element_rect(fill = "white", colour = "white"),
            plot.background = element_rect(fill = "white", colour = "white"),
            axis.text.x = element_text(angle = 90, hjust = 1, size = 8)) +
      labs(title = paste("Downregulated Lipid Genes in Cluster", cluster), x = "Log2 Fold Change", y = "Gene")
    ggsave(paste0("plots/downregulated_lipid_genes_cluster_", cluster, ".png"), plot = downregulated_plot, width = 10, height = 6)
    ggsave(paste0("plots/downregulated_lipid_genes_cluster_", cluster, ".svg"), plot = downregulated_plot, width = 10, height = 6)
    print(downregulated_plot)
  }
}


# Function to create volcano plot
create_volcano_plot <- function(markers, upregulated_genes, downregulated_genes, cluster) {
  markers <- markers %>% rownames_to_column(var = "gene")
  markers <- markers %>%
    mutate(color = case_when(
      p_val <= 0.05 & avg_log2FC > 0 ~ "Upregulated",
      p_val <= 0.05 & avg_log2FC < 0 ~ "Downregulated",
      TRUE ~ "Insignificant"
    )) %>%
    mutate(label = case_when(
      gene %in% upregulated_genes ~ gene,
      gene %in% downregulated_genes ~ gene,
      TRUE ~ ""
    ))
  
  volcano_plot <- ggplot(markers, aes(x = avg_log2FC, y = -log10(p_val), color = color)) +
    geom_point(alpha = 0.8) +
    scale_color_manual(values = c("Upregulated" = "pink", "Downregulated" = "skyblue", "Insignificant" = "grey")) +
    theme_minimal() +
    theme(panel.background = element_rect(fill = "white", colour = "white"),
          plot.background = element_rect(fill = "white", colour = "white")) +
    labs(title = paste("Volcano Plot for Cluster", cluster), x = "Log2 Fold Change", y = "-Log10 P-Value") +
    geom_text_repel(aes(label = label), size = 2, max.overlaps = 200, color = "black")  # Set label color to black
  
  return(volcano_plot)
}

# Create and save volcano plots for each cluster
for (cluster in names(cluster_markers)) {
  if (nrow(cluster_markers[[cluster]]) > 0) {
    volcano_plot <- create_volcano_plot(cluster_markers[[cluster]], upregulated_lipid_genes[[cluster]], downregulated_lipid_genes[[cluster]], cluster)
    ggsave(paste0("plots/volcano_plot_cluster_", cluster, ".png"), plot = volcano_plot, width = 10, height = 6)
    ggsave(paste0("plots/volcano_plot_cluster_", cluster, ".svg"), plot = volcano_plot, width = 10, height = 6)
  }
}


# Create heatmap for each cluster
for (cluster in names(upregulated_lipid_genes)) {
  # Combine upregulated and downregulated lipid genes
  significant_lipid_genes <- c(upregulated_lipid_genes[[cluster]], downregulated_lipid_genes[[cluster]])
  
  # Filter the count matrix to include only the significant lipid genes
  lipid_expression_matrix <- arranged_data3[rownames(arranged_data3) %in% significant_lipid_genes, ]
  
  if (nrow(lipid_expression_matrix) > 0) {
    # Generate the heatmap
    pheatmap(lipid_expression_matrix, 
             cluster_rows = TRUE, 
             cluster_cols = TRUE, 
             show_rownames = TRUE, 
             show_colnames = TRUE, 
             main = paste("Heatmap of Significant Lipid Genes in Cluster", cluster),
             color = colorRampPalette(c("skyblue", "white", "pink"))(50))
    
    # Save the heatmap
    ggsave(paste0("plots/heatmap_lipid_genes_cluster_", cluster, ".png"), width = 10, height = 8)
    ggsave(paste0("plots/heatmap_lipid_genes_cluster_", cluster, ".svg"), width = 10, height = 8)
  } else {
    cat("No significant lipid genes for cluster", cluster, "\n")
  }
}


# Function to create violin plots for top upregulated and downregulated lipid genes
create_violin_plot <- function(seurat_obj, genes, cluster, direction) {
  for (gene in genes) {
    plot <- VlnPlot(seurat_obj, features = gene, group.by = "condition") +
      labs(title = paste(direction, "Lipid Gene", gene, "in Cluster", cluster)) +
      theme_minimal()
    
    # Save as PNG
    ggsave(paste0('plots/',direction, "_lipid_gene_", gene, "_cluster_", cluster, ".png"), plot = plot, width = 10, height = 6)
    
    # Save as SVG
    ggsave(paste0('plots/',direction, "_lipid_gene_", gene, "_cluster_", cluster, ".svg"), plot = plot, width = 10, height = 6)
  }
}

# Function to get top n genes
get_top_genes <- function(genes, n = 4) {
  if (length(genes) >= n) {
    return(genes[1:n])
  } else {
    return(genes)
  }
}

# For each cluster, identify the top 4 upregulated and downregulated lipid genes
for (cluster in names(upregulated_lipid_genes)) {
  # cat("Processing cluster:", cluster, "\n")
  
  top_upregulated_genes <- get_top_genes(upregulated_lipid_genes[[cluster]], n = 4)
  top_downregulated_genes <- get_top_genes(downregulated_lipid_genes[[cluster]], n = 4)
  
  if (length(top_upregulated_genes) > 0) {
    create_violin_plot(seurat_obj, top_upregulated_genes, cluster, "Upregulated")
  } else {
    cat("No upregulated lipid genes for cluster", cluster, "\n")
  }
  
  if (length(top_downregulated_genes) > 0) {
    create_violin_plot(seurat_obj, top_downregulated_genes, cluster, "Downregulated")
  } else {
    cat("No downregulated lipid genes for cluster", cluster, "\n")
  }
}

# Function to create ridge plots for top upregulated and downregulated lipid genes
create_ridge_plot <- function(seurat_obj, genes, cluster, direction) {
  for (gene in genes) {
    plot <- RidgePlot(seurat_obj, features = gene, group.by = "condition") +
      labs(title = paste(direction, "Lipid Gene", gene, "in Cluster", cluster)) +
      theme_minimal()
    
    # Save as PNG
    ggsave(paste0('plots/',direction, "_lipid_gene_", gene, "_ridge_plot_cluster_", cluster, ".png"), plot = plot, width = 10, height = 6)
    
    # Save as SVG
    ggsave(paste0('plots/',direction, "_lipid_gene_", gene, "_ridge_plot_cluster_", cluster, ".svg"), plot = plot, width = 10, height = 6)
  }
}

# For each cluster, identify the top 4 upregulated and downregulated lipid genes
for (cluster in names(upregulated_lipid_genes)) {
  cat("Processing cluster:", cluster, "\n")
  
  top_upregulated_genes <- get_top_genes(upregulated_lipid_genes[[cluster]], n = 4)
  top_downregulated_genes <- get_top_genes(downregulated_lipid_genes[[cluster]], n = 4)
  
  if (length(top_upregulated_genes) > 0) {
    create_ridge_plot(seurat_obj, top_upregulated_genes, cluster, "Upregulated")
  } else {
    cat("No upregulated lipid genes for cluster", cluster, "\n")
  }
  
  if (length(top_downregulated_genes) > 0) {
    create_ridge_plot(seurat_obj, top_downregulated_genes, cluster, "Downregulated")
  } else {
    cat("No downregulated lipid genes for cluster", cluster, "\n")
  }
}

# Function to create feature plots for top upregulated and downregulated lipid genes
create_feature_plot <- function(seurat_obj, genes, cluster, direction) {
  for (gene in genes) {
    plot <- FeaturePlot(seurat_obj, features = gene, split.by = "condition") +
      labs(title = paste(direction, "Lipid Gene", gene, "in Cluster", cluster)) +
      theme_minimal()
    
    # Save as PNG
    ggsave(paste0('plots/',direction, "_lipid_gene_", gene, "_feature_plot_cluster_", cluster, ".png"), plot = plot, width = 10, height = 6)
    
    # Save as SVG
    ggsave(paste0('plots/',direction, "_lipid_gene_", gene, "_feature_plot_cluster_", cluster, ".svg"), plot = plot, width = 10, height = 6)
  }
}

# For each cluster, identify the top 4 upregulated and downregulated lipid genes
for (cluster in names(upregulated_lipid_genes)) {
  # cat("Processing cluster:", cluster, "\n")
  
  top_upregulated_genes <- get_top_genes(upregulated_lipid_genes[[cluster]], n = 4)
  top_downregulated_genes <- get_top_genes(downregulated_lipid_genes[[cluster]], n = 4)
  
  if (length(top_upregulated_genes) > 0) {
    create_feature_plot(seurat_obj, top_upregulated_genes, cluster, "Upregulated")
  } else {
    cat("No upregulated lipid genes for cluster", cluster, "\n")
  }
  
  if (length(top_downregulated_genes) > 0) {
    create_feature_plot(seurat_obj, top_downregulated_genes, cluster, "Downregulated")
  } else {
    cat("No downregulated lipid genes for cluster", cluster, "\n")
  }
}


# Function to create dot plots for upregulated and downregulated lipid genes
create_dot_plot <- function(seurat_obj, genes, cluster, direction) {
  if (length(genes) > 0) {
    plot <- DotPlot(seurat_obj, features = genes, group.by = "condition") +
      labs(title = paste(direction, "Lipid Genes in Cluster", cluster)) +
      theme_minimal() +
      theme(panel.background = element_rect(fill = "white", colour = "white"),
            plot.background = element_rect(fill = "white", colour = "white"),
            axis.text.x = element_text(angle = 90, hjust = 1, size = 8))  # Adjust the text angle and size of gene labels
    
    # Save as PNG
    ggsave(paste0('plots/',direction, "_lipid_genes_dot_plot_cluster_", cluster, ".png"), plot = plot, width = 10, height = 6)
    
    # Save as SVG
    ggsave(paste0('plots/',direction, "_lipid_genes_dot_plot_cluster_", cluster, ".svg"), plot = plot, width = 10, height = 6)
  } else {
    cat("No", direction, "lipid genes for cluster", cluster, "\n")
  }
}

# For each cluster, create dot plots for all upregulated and downregulated lipid genes
for (cluster in names(upregulated_lipid_genes)) {
  cat("Processing cluster:", cluster, "\n")
  
  upregulated_genes <- upregulated_lipid_genes[[cluster]]
  downregulated_genes <- downregulated_lipid_genes[[cluster]]
  
  create_dot_plot(seurat_obj, upregulated_genes, cluster, "Upregulated")
  create_dot_plot(seurat_obj, downregulated_genes, cluster, "Downregulated")
}