# Install necessary libraries if not already installed
if (!requireNamespace("svglite", quietly = TRUE)) {
  install.packages("svglite")
}
if (!requireNamespace("ggridges", quietly = TRUE)) {
  install.packages("ggridges")
}
if (!requireNamespace("pheatmap", quietly = TRUE)) {
  install.packages("pheatmap")
}
if (!requireNamespace("ggrepel", quietly = TRUE)) {
  install.packages("ggrepel")
}

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

########################################################################

args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
  stop("No session folder path provided.")
}
session_folder <- args[1]
base_path <- "D:/Raylab/NewNetwork"
session_path <- file.path(base_path,session_folder)

# session_path <- "D:/Raylab/NewNetwork/rScript/sessions/20ea8aaf-e725-43d2-989c-c6b63b50d647"
setwd(session_path)

dir.create(file.path(session_path,"plots"), recursive = TRUE, showWarnings = FALSE)
###########################################################################################

# Function to save plots in both PNG and SVG formats
save_plot <- function(plot, filename_base) {
  # Save PNG
  ggsave(filename = paste0(filename_base, ".png"), plot = plot, width = 10, height = 6, dpi = 600)
  # Save SVG
  svglite(filename = paste0(filename_base, ".svg"), width = 10, height = 6)
  print(plot)
  dev.off()  # Close the SVG device
}

# Data Loading
arranged_data3 <- read.csv("scRNAseq_expression_matrix.csv", row.names = NULL)

if (any(duplicated(rownames(arranged_data3)))) {
  cat("Found duplicate Genes")
}

arranged_data3 <- arranged_data3[!duplicated(arranged_data3$Gene), ]

head(arranged_data3)
rownames(arranged_data3) <- arranged_data3$Gene
arranged_data3 <- arranged_data3[,-1]

metadata2 <- read.csv("metadata.csv", row.names = 1)

# head(arranged_data3)
# head(metadata2)

metadata2_rownames <- rownames(metadata2)
arranged_data3_colnames <- colnames(arranged_data3)
matches <- metadata2_rownames %in% arranged_data3_colnames

if (!all(matches)) {
  stop("Mismatch between metadata row names and expression data column names.")
}

# Ensure the column "Condition" exists
if (!"Condition" %in% colnames(metadata2)) {
  stop("Column 'Condition' not found in the metadata.")
}

###############################################################################################
#To Visualize the distribution of expression level of genes in two conditions 
# Calculate the mean expression level for each gene
mean_expression <- rowMeans(arranged_data3)

# Select the top 10 genes based on mean expression levels
top_genes <- names(sort(mean_expression, decreasing = TRUE))[1:10]

# Merge the count matrix with metadata
merged_data <- t(arranged_data3)
merged_data <- data.frame(merged_data)
merged_data$SampleID <- rownames(merged_data)
merged_data <- merge(merged_data, metadata2, by.x = "SampleID", by.y = "row.names")

# Melt the data for easier plotting with ggplot2
melted_data <- melt(merged_data, id.vars = c("SampleID", "Condition"))

# Select the top 10 genes for visualization
subset_data <- melted_data[melted_data$variable %in% top_genes, ]

# Plotting the data
box_plot <- ggplot(subset_data, aes(x = variable, y = value, fill = Condition)) +
  geom_boxplot() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Gene Expression Levels for Top 10 Genes",
       x = "Gene",
       y = "Expression",
       fill = "Condition")
# print(box_plot)
save_plot(box_plot, "plots/box_plot_top_10_genes")

###############################################################################################

# Create Seurat Object
gene_ids <- rownames(arranged_data3)
seurat_obj <- CreateSeuratObject(counts = arranged_data3, meta.data = metadata2)
seurat_obj <- NormalizeData(seurat_obj)
# cat("Here")
# print(seurat_obj@meta.data)
# head(seurat_obj@assays)

# Identify mitochondrial genes
mito_genes <- grep("^MT-", rownames(seurat_obj), value = TRUE)
if (length(mito_genes) == 0) {
  mito_genes <- grep("^mt-", rownames(seurat_obj), value = TRUE)
}

# Calculate percent.mt if mitochondrial genes are found
if (length(mito_genes) > 0) {
  seurat_obj[["percent.mt"]] <- PercentageFeatureSet(seurat_obj, pattern = "^MT-")
  # Violin plots with percent.mt
  vln_plot1 <- VlnPlot(seurat_obj, features = c("nFeature_RNA", "nCount_RNA", "percent.mt"), ncol = 3)
  vln_plot2 <- VlnPlot(seurat_obj, features = c("nFeature_RNA", "nCount_RNA", "percent.mt"), group.by = "Condition", ncol = 3) + theme(axis.text.x = element_text(angle = 45, hjust = 1))
} else {
  # Violin plots without percent.mt
  vln_plot1 <- VlnPlot(seurat_obj, features = c("nFeature_RNA", "nCount_RNA"), ncol = 2)
  vln_plot2 <- VlnPlot(seurat_obj, features = c("nFeature_RNA", "nCount_RNA"), group.by = "Condition", ncol = 2) + theme(axis.text.x = element_text(angle = 45, hjust = 1))
}

print(vln_plot1)
print(vln_plot2)
save_plot(vln_plot1, "plots/vln_plot1")
save_plot(vln_plot2, "plots/vln_plot2")

# Scatter plot
scatter_plot <- FeatureScatter(seurat_obj, feature1 = "nCount_RNA", feature2 = "nFeature_RNA")
print(scatter_plot)
save_plot(scatter_plot, "plots/scatter_plot")

# Find variable genes
seurat_obj <- FindVariableFeatures(seurat_obj)

# Variable feature plots
top10 <- head(VariableFeatures(seurat_obj), 10)
plot1 <- VariableFeaturePlot(seurat_obj)
plot2 <- LabelPoints(plot = plot1, points = top10, repel = TRUE)
# print(plot2)
save_plot(plot1, "plots/variable_feature_plot1")
save_plot(plot2, "plots/variable_feature_plot2")

# Scaling of the Data
seurat_obj <- ScaleData(seurat_obj)

# Ensure the default assay is set to "RNA"
DefaultAssay(seurat_obj) <- "RNA"

# Retrieve the data matrix
data_matrix <- GetAssayData(seurat_obj, slot = "counts")

# Check the dimensions of the data matrix
num_features <- nrow(data_matrix)
num_cells <- ncol(data_matrix)

# Determine the maximum number of PCs that can be computed
max_pcs <- min(num_features, num_cells) - 1

# Run PCA with the appropriate number of PCs
seurat_obj <- RunPCA(seurat_obj, features = VariableFeatures(object = seurat_obj), npcs = max_pcs)

# Plot the elbow plot to visualize the variance explained by each PC
elbow_plot <- ElbowPlot(seurat_obj)
print(elbow_plot)
save_plot(elbow_plot, "plots/elbow_plot")

# Print the PCA object to see the variance explained by each PC
# print(seurat_obj[["pca"]], dims = 1:10, nfeatures = 5)

# Check the number of available cells
num_cells <- ncol(seurat_obj)

# Determine the number of cells to use for heatmaps (minimum of 100 or available cells)
cells_to_use <- min(100, num_cells)

for (i in 1:10) {
  # Use base R functions to open graphic devices
  png(filename = paste0("plots/dim_heatmap_plot_", i, ".png"), width = 1000, height = 1000, res = 300)
  DimHeatmap(seurat_obj, dims = i, cells = cells_to_use, balanced = TRUE)
  dev.off()  # Close the PNG device
  
  svglite(filename = paste0("plots/dim_heatmap_plot_", i, ".svg"), width = 10, height = 10)
  DimHeatmap(seurat_obj, dims = i, cells = cells_to_use, balanced = TRUE)
  dev.off()  # Close the SVG device
}

# VizDimLoadings
viz_dim_loadings <- VizDimLoadings(seurat_obj, dims = 1:2, reduction = "pca")
print(viz_dim_loadings)
save_plot(viz_dim_loadings, "plots/viz_dim_loadings")

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
  save_plot(plot, paste0("plots/PC_", i, "_top_10_genes"))
}

# Perform clustering on the Seurat object
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:10)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)
seurat_obj@meta.data

# Run UMAP on clusters
num_cells <- ncol(seurat_obj)

# Set a reasonable value for n_neighbors
n_neighbors <- min(20, num_cells - 1)  # Adjust this number based on your dataset size

# Run UMAP with adjusted n_neighbors
seurat_obj <- RunUMAP(seurat_obj, dims = 1:10, n.neighbors = n_neighbors)

# Create a UMAP plot
umap_plot <- DimPlot(seurat_obj, reduction = "umap", group.by = "seurat_clusters")

# Print and save the plot
print(umap_plot)
save_plot(umap_plot, "plots/umap_plot")
seurat_obj@meta.data

# Ensure the 'Condition' column is a factor
seurat_obj@meta.data$Condition <- factor(seurat_obj@meta.data$Condition)
# Define the function to perform DE analysis within a cluster
perform_DE_analysis_within_cluster <- function(seurat_obj, cluster) {
  # Subset the Seurat object to only include cells from the specified cluster
  cells_in_cluster <- WhichCells(seurat_obj, idents = cluster)
  seurat_cluster <- subset(seurat_obj, cells = cells_in_cluster)
  # Assign identities based on Condition for the subset
  seurat_cluster <- SetIdent(seurat_cluster, value = "Condition")
  
  # Perform DE analysis: 'diseased' vs 'normal'
  DE_results <- FindMarkers(seurat_cluster, ident.1 = "diseased", ident.2 = "normal", min.pct = 0.25, logfc.threshold = 0.1)
  
  return(DE_results)
}
# Get the unique clusters from the Seurat object
clusters <- unique(seurat_obj$seurat_clusters)
cluster_markers <- list()
# Loop through each cluster and perform DE analysis
for (cluster in clusters) {
  # cat("Performing DE analysis for cluster:", cluster, "\n")
  
  # Set identities to clusters for proper subsetting
  seurat_obj <- SetIdent(seurat_obj, value = "seurat_clusters")
  
  # Perform DE analysis within the cluster
  cluster_markers[[as.character(cluster)]] <- perform_DE_analysis_within_cluster(seurat_obj, cluster)
  
  # cat("Top markers for cluster", cluster, "\n")
  # print(head(cluster_markers[[as.character(cluster)]]))
}

# Optionally, save the results for each cluster
save(cluster_markers, file = "cluster_markers.RData")
cluster_markers

# Load lipid genes
lipid_genes <- read.csv("D:/Raylab/NewNetwork/rScript/lipid_genes.csv", header = TRUE, stringsAsFactors = FALSE)
lipid_gene_symbols <- lipid_genes[[1]]

# Initialize lists to store upregulated and downregulated lipid genes for each cluster
upregulated_lipid_genes <- list()
downregulated_lipid_genes <- list()

# Cutoff values
cutoff_p_val <- 0.05  # p-value cutoff
cutoff_log2FC <- 0.1  # log2 fold change cutoff

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
      
      # Print the results for this cluster
      # cat("Upregulated lipid genes for cluster", cluster, ":\n")
      # print(upregulated_lipid_genes[[cluster]])
      # cat("Downregulated lipid genes for cluster", cluster, ":\n")
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
# Print the final results
# cat("Upregulated Lipid Genes in Each Cluster:\n")
# print(upregulated_lipid_genes)

# cat("Downregulated Lipid Genes in Each Cluster:\n")
# print(downregulated_lipid_genes)

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

# Print the data frames for plotting
# cat("Data for plotting upregulated lipid genes:\n")
# print(upregulated_data)

# cat("Data for plotting downregulated lipid genes:\n")
# print(downregulated_data)

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
    geom_text_repel(aes(label = label), size = 2, max.overlaps = 200, color = "black")
  
  return(volcano_plot)
}


  # Function to create and save various plots with white background
  create_and_save_plots <- function(seurat_obj, genes, cluster, plot_type) {
    if (length(genes) > 0) {
      if (plot_type == "feature") {
        plot <- FeaturePlot(seurat_obj, features = genes, combine = FALSE) 
      } else if (plot_type == "violin") {
        plot <- VlnPlot(seurat_obj, features = genes, combine = FALSE)
      } else if (plot_type == "dot") {
        plot <- DotPlot(seurat_obj, features = genes) + theme_minimal() +
          theme(panel.background = element_rect(fill = "white", colour = "white"),
                plot.background = element_rect(fill = "white", colour = "white"))
      } else if (plot_type == "ridge") {
        plot <- RidgePlot(seurat_obj, features = genes, combine = FALSE)
      }
      
      if (plot_type %in% c("feature", "violin", "ridge")) {
        for (i in seq_along(plot)) {
          plot[[i]] <- plot[[i]] + theme_minimal() +
            theme(panel.background = element_rect(fill = "white", colour = "white"),
                  plot.background = element_rect(fill = "white", colour = "white"))
          ggsave(paste0('plots/',plot_type, "_plot_cluster_", cluster, "_gene_", genes[i], ".png"), plot = plot[[i]], width = 10, height = 6)
          ggsave(paste0('plots/',plot_type, "_plot_cluster_", cluster, "_gene_", genes[i], ".svg"), plot = plot[[i]], width = 10, height = 6)
        }
      } else {
        ggsave(paste0('plots/',plot_type, "_plot_cluster_", cluster, ".png"), plot = plot, width = 10, height = 6)
        ggsave(paste0('plots/',plot_type, "_plot_cluster_", cluster, ".svg"), plot = plot, width = 10, height = 6)
      }
    }
  }
  
  # Create and save plots for each cluster
  for (cluster in names(upregulated_lipid_genes)) {
    if (length(upregulated_lipid_genes[[cluster]]) > 0) {
      create_and_save_plots(seurat_obj, upregulated_lipid_genes[[cluster]], cluster, "feature")
      create_and_save_plots(seurat_obj, upregulated_lipid_genes[[cluster]], cluster, "violin")
      create_and_save_plots(seurat_obj, upregulated_lipid_genes[[cluster]], cluster, "dot")
      create_and_save_plots(seurat_obj, upregulated_lipid_genes[[cluster]], cluster, "ridge")
    }
    
    if (length(downregulated_lipid_genes[[cluster]]) > 0) {
      create_and_save_plots(seurat_obj, downregulated_lipid_genes[[cluster]], cluster, "feature")
      create_and_save_plots(seurat_obj, downregulated_lipid_genes[[cluster]], cluster, "violin")
      create_and_save_plots(seurat_obj, downregulated_lipid_genes[[cluster]], cluster, "dot")
      create_and_save_plots(seurat_obj, downregulated_lipid_genes[[cluster]], cluster, "ridge")
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
      heatmap_plot <- pheatmap(lipid_expression_matrix, 
                               cluster_rows = TRUE, 
                               cluster_cols = TRUE, 
                               show_rownames = TRUE, 
                               show_colnames = TRUE, 
                               main = paste("Heatmap of Significant Lipid Genes in Cluster", cluster), 
                               color = colorRampPalette(c("skyblue", "white", "pink"))(50))
      
      # Save the heatmap as PNG
      png(filename = paste0("plots/heatmap_lipid_genes_cluster_", cluster, ".png"), width = 10, height = 8, units = "in", res = 300)
      grid.draw(heatmap_plot$gtable)
      dev.off()  # Close the PNG device
      
      # Save the heatmap as SVG
      svglite(filename = paste0("plots/heatmap_lipid_genes_cluster_", cluster, ".svg"), width = 10, height = 8)
      grid.draw(heatmap_plot$gtable)
      dev.off()  # Close the SVG device
    } else {
      # cat("No significant lipid genes for cluster", cluster, "\n")
    }
  }


 
 
