import React, { useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  useToast,
  Progress,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
} from '@chakra-ui/react';
import { useDropzone } from 'react-dropzone';

const InvoiceUpload = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const toast = useToast();

  const onDrop = (acceptedFiles) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg']
    }
  });

  const handleUpload = async () => {
    setUploading(true);
    setProgress(0);

    try {
      for (let i = 0; i < files.length; i++) {
        const formData = new FormData();
        formData.append('file', files[i]);

        const response = await fetch('http://localhost:8000/invoices/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Failed to upload ${files[i].name}`);
        }

        setProgress(((i + 1) / files.length) * 100);
      }

      toast({
        title: 'Upload Successful',
        description: 'All files have been uploaded successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      setFiles([]);
    } catch (error) {
      toast({
        title: 'Upload Failed',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <VStack spacing={8} align="stretch">
      <Heading size="lg">Upload Invoices</Heading>
      
      <Box
        {...getRootProps()}
        p={10}
        border="2px dashed"
        borderColor={isDragActive ? 'blue.400' : 'gray.200'}
        borderRadius="md"
        textAlign="center"
        cursor="pointer"
        _hover={{ borderColor: 'blue.400' }}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <Text>Drop the files here...</Text>
        ) : (
          <Text>Drag and drop invoice files here, or click to select files</Text>
        )}
      </Box>

      {files.length > 0 && (
        <VStack spacing={4} align="stretch">
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>File Name</Th>
                <Th>Size</Th>
                <Th>Type</Th>
              </Tr>
            </Thead>
            <Tbody>
              {files.map((file, index) => (
                <Tr key={index}>
                  <Td>{file.name}</Td>
                  <Td>{(file.size / 1024).toFixed(2)} KB</Td>
                  <Td>{file.type}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>

          {uploading && (
            <Progress value={progress} size="sm" colorScheme="blue" />
          )}

          <Button
            colorScheme="blue"
            onClick={handleUpload}
            isLoading={uploading}
            loadingText="Uploading..."
          >
            Upload {files.length} File{files.length !== 1 ? 's' : ''}
          </Button>
        </VStack>
      )}
    </VStack>
  );
};

export default InvoiceUpload; 