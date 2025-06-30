import React, { useState, useCallback } from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Button,
  useToast,
  Progress,
  Card,
  CardBody,
  CardHeader,
  HStack,
  Icon,
  Badge,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Grid,
  GridItem,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Spinner,
  Divider,
} from '@chakra-ui/react';
import { useDropzone } from 'react-dropzone';
import { FiUpload, FiFileText, FiCheckCircle, FiAlertCircle, FiClock } from 'react-icons/fi';

const InvoiceUpload = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [processingResults, setProcessingResults] = useState(null);
  const toast = useToast();

  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const hoverBg = useColorModeValue('gray.50', 'gray.600');

  const onDrop = useCallback((acceptedFiles) => {
    setFiles(acceptedFiles);
    setError(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  const handleUpload = async () => {
    setUploading(true);
    setProgress(0);
    setError(null);
    setProcessingResults(null);

    try {
      for (let i = 0; i < files.length; i++) {
        const formData = new FormData();
        formData.append('file', files[i]);

        console.log('Uploading file:', files[i].name);

        // Upload file
        const uploadResponse = await fetch('http://localhost:8000/api/v1/invoices/upload', {
          method: 'POST',
          body: formData,
        });

        console.log('Upload response status:', uploadResponse.status);
        const uploadData = await uploadResponse.json();
        console.log('Upload response data:', uploadData);

        if (!uploadResponse.ok) {
          throw new Error(uploadData.detail || `Failed to upload ${files[i].name}`);
        }

        console.log('Processing invoice:', uploadData.invoice_id);

        // Process invoice with all services
        const processResponse = await fetch(`http://localhost:8000/api/v1/invoices/${uploadData.invoice_id}/process`, {
          method: 'POST',
        });

        console.log('Process response status:', processResponse.status);
        const processData = await processResponse.json();
        console.log('Process response data:', processData);

        if (!processResponse.ok) {
          throw new Error(processData.detail || `Failed to process ${files[i].name}`);
        }

        // Update processing results
        setProcessingResults({
          ocr: {
            invoice_number: processData.ocr?.invoice_number || 'N/A',
            receipt_number: processData.ocr?.receipt_number || 'N/A',
            date: processData.ocr?.date || 'N/A',
            time: processData.ocr?.time || 'N/A',
            vendor: processData.ocr?.vendor || 'N/A',
            vendor_address: processData.ocr?.vendor_address || 'N/A',
            vendor_phone: processData.ocr?.vendor_phone || 'N/A',
            vendor_fax: processData.ocr?.vendor_fax || 'N/A',
            amount: processData.ocr?.amount || 0,
            subtotal: processData.ocr?.subtotal || 0,
            discount: processData.ocr?.discount || 0,
            gst_amount: processData.ocr?.gst_amount || 0,
            salesperson: processData.ocr?.salesperson || 'N/A',
            cashier: processData.ocr?.cashier || 'N/A',
            items: processData.ocr?.items || [],
            confidence: processData.ocr?.confidence || 0,
            raw_text: processData.ocr?.raw_text || 'No text extracted'
          },
          gst: {
            gstin: processData.gst?.gstin || 'N/A',
            hsn_code: processData.gst?.hsn_code || 'N/A',
            category: processData.gst?.category || 'N/A',
            tax_rate: processData.gst?.tax_rate || 0,
            status: processData.gst?.status || 'pending'
          },
          reconciliation: {
            matched_amount: processData.reconciliation?.matched_amount || 0,
            discrepancy: processData.reconciliation?.discrepancy || 0,
            confidence: processData.reconciliation?.confidence || 0,
            status: processData.reconciliation?.status || 'pending'
          },
          fraud: {
            risk_score: processData.fraud?.risk_score || 0,
            risk_level: processData.fraud?.risk_level || 'low',
            alerts: processData.fraud?.alerts || []
          }
        });

        setProgress(((i + 1) / files.length) * 100);
      }

      toast({
        title: 'Upload Successful',
        description: 'All files have been uploaded and processed successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      setFiles([]);
    } catch (error) {
      console.error('Upload error:', error);
      setError(error.message);
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

  const getServiceStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'green';
      case 'warning':
        return 'yellow';
      case 'error':
        return 'red';
      default:
        return 'gray';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
    }).format(amount);
  };

  return (
    <Box p={4}>
      <VStack spacing={8} align="stretch">
        <Heading size="lg">Upload Invoice</Heading>

        {/* Upload Area */}
        <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
          <CardBody>
            <VStack spacing={4}>
              <Box
                {...getRootProps()}
                p={10}
                border="2px dashed"
                borderColor={isDragActive ? 'blue.500' : 'gray.200'}
                borderRadius="md"
                textAlign="center"
                cursor="pointer"
                _hover={{ borderColor: 'blue.500' }}
                transition="all 0.2s"
              >
                <input {...getInputProps()} />
                <Icon as={FiUpload} w={10} h={10} color="gray.400" mb={4} />
                <Text fontSize="lg" mb={2}>
                  {isDragActive
                    ? 'Drop the files here...'
                    : 'Drag and drop files here, or click to select files'}
                </Text>
                <Text fontSize="sm" color="gray.500">
                  Supported formats: PDF, JPEG, PNG (max 10MB)
                </Text>
              </Box>

              {files.length > 0 && (
                <VStack spacing={2} align="stretch" w="100%">
                  {files.map((file, index) => (
                    <HStack
                      key={index}
                      p={3}
                      borderWidth="1px"
                      borderRadius="md"
                      borderColor={borderColor}
                      justify="space-between"
                    >
                      <HStack>
                        <Icon as={FiFileText} />
                        <Text>{file.name}</Text>
                      </HStack>
                      <Text color="gray.500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </Text>
                    </HStack>
                  ))}
                </VStack>
              )}

              {uploading && (
                <Box w="100%">
                  <Progress value={progress} size="sm" colorScheme="blue" mb={2} />
                  <Text fontSize="sm" color="gray.500" textAlign="center">
                    Uploading... {Math.round(progress)}%
                  </Text>
                </Box>
              )}

              {error && (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <Box flex="1">
                    <AlertTitle>Upload Failed</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                  </Box>
                </Alert>
              )}

              <Button
                colorScheme="blue"
                onClick={handleUpload}
                isLoading={uploading}
                loadingText="Uploading..."
                isDisabled={files.length === 0 || uploading}
                w="100%"
                size="lg"
              >
                Upload and Process
              </Button>
            </VStack>
          </CardBody>
        </Card>

        {/* Processing Results */}
        {processingResults && (
          <Card bg={cardBg} borderColor={borderColor} borderWidth="1px">
            <CardHeader>
              <Heading size="md">Processing Results</Heading>
            </CardHeader>
            <CardBody>
              <Tabs variant="enclosed" colorScheme="blue">
                <TabList>
                  <Tab>OCR Results</Tab>
                  <Tab>Raw OCR Text</Tab>
                  <Tab>GST Analysis</Tab>
                  <Tab>Reconciliation</Tab>
                  <Tab>Fraud Detection</Tab>
                </TabList>

                <TabPanels>
                  {/* OCR Results */}
                  <TabPanel>
                    <VStack spacing={6} align="stretch">
                      {/* Basic Information */}
                      <Box>
                        <Heading size="sm" mb={4} color="blue.600">Basic Information</Heading>
                        <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                          <GridItem>
                            <Stat>
                              <StatLabel>Invoice Number</StatLabel>
                              <StatNumber fontSize="lg">{processingResults.ocr?.invoice_number || 'N/A'}</StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem>
                            <Stat>
                              <StatLabel>Receipt Number</StatLabel>
                              <StatNumber fontSize="lg">{processingResults.ocr?.receipt_number || 'N/A'}</StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem>
                            <Stat>
                              <StatLabel>Date</StatLabel>
                              <StatNumber fontSize="lg">{processingResults.ocr?.date || 'N/A'}</StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem>
                            <Stat>
                              <StatLabel>Time</StatLabel>
                              <StatNumber fontSize="lg">{processingResults.ocr?.time || 'N/A'}</StatNumber>
                            </Stat>
                          </GridItem>
                        </Grid>
                      </Box>

                      <Divider />

                      {/* Vendor Information */}
                      <Box>
                        <Heading size="sm" mb={4} color="blue.600">Vendor Information</Heading>
                        <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                          <GridItem colSpan={2}>
                            <Stat>
                              <StatLabel>Vendor Name</StatLabel>
                              <StatNumber fontSize="lg">{processingResults.ocr?.vendor || 'N/A'}</StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem colSpan={2}>
                            <Stat>
                              <StatLabel>Address</StatLabel>
                              <StatNumber fontSize="md">{processingResults.ocr?.vendor_address || 'N/A'}</StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem>
                            <Stat>
                              <StatLabel>Phone</StatLabel>
                              <StatNumber fontSize="lg">{processingResults.ocr?.vendor_phone || 'N/A'}</StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem>
                            <Stat>
                              <StatLabel>Fax</StatLabel>
                              <StatNumber fontSize="lg">{processingResults.ocr?.vendor_fax || 'N/A'}</StatNumber>
                            </Stat>
                          </GridItem>
                        </Grid>
                      </Box>

                      <Divider />

                      {/* Amount Information */}
                      <Box>
                        <Heading size="sm" mb={4} color="blue.600">Amount Details</Heading>
                        <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                          <GridItem>
                            <Stat>
                              <StatLabel>Total Amount</StatLabel>
                              <StatNumber fontSize="lg" color="green.600">
                                {processingResults.ocr?.amount
                                  ? formatCurrency(processingResults.ocr.amount)
                                  : 'N/A'}
                              </StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem>
                            <Stat>
                              <StatLabel>Subtotal</StatLabel>
                              <StatNumber fontSize="lg">
                                {processingResults.ocr?.subtotal
                                  ? formatCurrency(processingResults.ocr.subtotal)
                                  : 'N/A'}
                              </StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem>
                            <Stat>
                              <StatLabel>Discount</StatLabel>
                              <StatNumber fontSize="lg" color="orange.600">
                                {processingResults.ocr?.discount
                                  ? formatCurrency(processingResults.ocr.discount)
                                  : 'N/A'}
                              </StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem>
                            <Stat>
                              <StatLabel>GST Amount</StatLabel>
                              <StatNumber fontSize="lg" color="purple.600">
                                {processingResults.ocr?.gst_amount
                                  ? formatCurrency(processingResults.ocr.gst_amount)
                                  : 'N/A'}
                              </StatNumber>
                            </Stat>
                          </GridItem>
                        </Grid>
                      </Box>

                      <Divider />

                      {/* Staff Information */}
                      <Box>
                        <Heading size="sm" mb={4} color="blue.600">Staff Information</Heading>
                        <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                          <GridItem>
                            <Stat>
                              <StatLabel>Salesperson</StatLabel>
                              <StatNumber fontSize="lg">{processingResults.ocr?.salesperson || 'N/A'}</StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem>
                            <Stat>
                              <StatLabel>Cashier</StatLabel>
                              <StatNumber fontSize="lg">{processingResults.ocr?.cashier || 'N/A'}</StatNumber>
                            </Stat>
                          </GridItem>
                        </Grid>
                      </Box>

                      {/* Item Details */}
                      {processingResults.ocr?.items && processingResults.ocr.items.length > 0 && (
                        <>
                          <Divider />
                          <Box>
                            <Heading size="sm" mb={4} color="blue.600">Item Details</Heading>
                            <Box
                              borderWidth="1px"
                              borderRadius="md"
                              borderColor={borderColor}
                              overflow="hidden"
                            >
                              <Box
                                bg={useColorModeValue('gray.50', 'gray.700')}
                                px={4}
                                py={2}
                                borderBottomWidth="1px"
                                borderColor={borderColor}
                              >
                                <Grid templateColumns="1fr 2fr 1fr" gap={4}>
                                  <Text fontWeight="bold">Code</Text>
                                  <Text fontWeight="bold">Description</Text>
                                  <Text fontWeight="bold">Amount</Text>
                                </Grid>
                              </Box>
                              {processingResults.ocr.items.map((item, index) => (
                                <Box
                                  key={index}
                                  px={4}
                                  py={3}
                                  borderBottomWidth={index < processingResults.ocr.items.length - 1 ? "1px" : "0"}
                                  borderColor={borderColor}
                                  _hover={{ bg: useColorModeValue('gray.50', 'gray.600') }}
                                >
                                  <Grid templateColumns="1fr 2fr 1fr" gap={4}>
                                    <Text fontSize="sm" fontFamily="mono">{item.code}</Text>
                                    <Text fontSize="sm">{item.description}</Text>
                                    <Text fontSize="sm" fontWeight="bold">
                                      {formatCurrency(item.amount)}
                                    </Text>
                                  </Grid>
                                </Box>
                              ))}
                            </Box>
                          </Box>
                        </>
                      )}

                      <Divider />

                      {/* Confidence Score */}
                      <HStack justify="space-between" p={4} bg={useColorModeValue('blue.50', 'blue.900')} borderRadius="md">
                        <Text fontWeight="bold">OCR Confidence Score</Text>
                        <Badge colorScheme="green" fontSize="md" px={3} py={1}>
                          {processingResults.ocr?.confidence || 'N/A'}%
                        </Badge>
                      </HStack>
                    </VStack>
                  </TabPanel>

                  {/* Raw OCR Text */}
                  <TabPanel>
                    <VStack spacing={4} align="stretch">
                      <Box>
                        <Heading size="sm" mb={4} color="blue.600">Extracted Text</Heading>
                        <Box
                          p={4}
                          bg={useColorModeValue('gray.50', 'gray.700')}
                          borderRadius="md"
                          borderWidth="1px"
                          borderColor={borderColor}
                          maxH="400px"
                          overflowY="auto"
                        >
                          <Text
                            fontFamily="mono"
                            fontSize="sm"
                            whiteSpace="pre-wrap"
                            wordBreak="break-word"
                          >
                            {processingResults.ocr?.raw_text || 'No text extracted'}
                          </Text>
                        </Box>
                      </Box>
                      
                      <Box>
                        <Heading size="sm" mb={4} color="blue.600">Text Statistics</Heading>
                        <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                          <GridItem>
                            <Stat>
                              <StatLabel>Characters</StatLabel>
                              <StatNumber fontSize="lg">
                                {processingResults.ocr?.raw_text ? processingResults.ocr.raw_text.length : 0}
                              </StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem>
                            <Stat>
                              <StatLabel>Words</StatLabel>
                              <StatNumber fontSize="lg">
                                {processingResults.ocr?.raw_text ? processingResults.ocr.raw_text.split(/\s+/).length : 0}
                              </StatNumber>
                            </Stat>
                          </GridItem>
                          <GridItem>
                            <Stat>
                              <StatLabel>Lines</StatLabel>
                              <StatNumber fontSize="lg">
                                {processingResults.ocr?.raw_text ? processingResults.ocr.raw_text.split('\n').length : 0}
                              </StatNumber>
                            </Stat>
                          </GridItem>
                        </Grid>
                      </Box>
                    </VStack>
                  </TabPanel>

                  {/* GST Analysis */}
                  <TabPanel>
                    <VStack spacing={4} align="stretch">
                      <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                        <GridItem>
                          <Stat>
                            <StatLabel>GSTIN</StatLabel>
                            <StatNumber>{processingResults.gst?.gstin || 'N/A'}</StatNumber>
                          </Stat>
                        </GridItem>
                        <GridItem>
                          <Stat>
                            <StatLabel>HSN Code</StatLabel>
                            <StatNumber>{processingResults.gst?.hsn_code || 'N/A'}</StatNumber>
                          </Stat>
                        </GridItem>
                        <GridItem>
                          <Stat>
                            <StatLabel>Category</StatLabel>
                            <StatNumber>{processingResults.gst?.category || 'N/A'}</StatNumber>
                          </Stat>
                        </GridItem>
                        <GridItem>
                          <Stat>
                            <StatLabel>Tax Rate</StatLabel>
                            <StatNumber>{processingResults.gst?.tax_rate || 'N/A'}%</StatNumber>
                          </Stat>
                        </GridItem>
                      </Grid>
                      <Divider />
                      <HStack justify="space-between">
                        <Text>Validation Status</Text>
                        <Badge colorScheme={getServiceStatusColor(processingResults.gst?.status)}>
                          {processingResults.gst?.status || 'N/A'}
                        </Badge>
                      </HStack>
                    </VStack>
                  </TabPanel>

                  {/* Reconciliation */}
                  <TabPanel>
                    <VStack spacing={4} align="stretch">
                      <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                        <GridItem>
                          <Stat>
                            <StatLabel>Matched Amount</StatLabel>
                            <StatNumber>
                              {processingResults.reconciliation?.matched_amount
                                ? formatCurrency(processingResults.reconciliation.matched_amount)
                                : 'N/A'}
                            </StatNumber>
                          </Stat>
                        </GridItem>
                        <GridItem>
                          <Stat>
                            <StatLabel>Discrepancy</StatLabel>
                            <StatNumber>
                              {processingResults.reconciliation?.discrepancy
                                ? formatCurrency(processingResults.reconciliation.discrepancy)
                                : 'N/A'}
                            </StatNumber>
                          </Stat>
                        </GridItem>
                        <GridItem>
                          <Stat>
                            <StatLabel>Match Confidence</StatLabel>
                            <StatNumber>
                              {processingResults.reconciliation?.confidence || 'N/A'}%
                            </StatNumber>
                          </Stat>
                        </GridItem>
                        <GridItem>
                          <Stat>
                            <StatLabel>Status</StatLabel>
                            <StatNumber>
                              <Badge colorScheme={getServiceStatusColor(processingResults.reconciliation?.status)}>
                                {processingResults.reconciliation?.status || 'N/A'}
                              </Badge>
                            </StatNumber>
                          </Stat>
                        </GridItem>
                      </Grid>
                    </VStack>
                  </TabPanel>

                  {/* Fraud Detection */}
                  <TabPanel>
                    <VStack spacing={4} align="stretch">
                      <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                        <GridItem>
                          <Stat>
                            <StatLabel>Risk Score</StatLabel>
                            <StatNumber>{processingResults.fraud?.risk_score || 'N/A'}</StatNumber>
                          </Stat>
                        </GridItem>
                        <GridItem>
                          <Stat>
                            <StatLabel>Risk Level</StatLabel>
                            <StatNumber>
                              <Badge colorScheme={getServiceStatusColor(processingResults.fraud?.risk_level)}>
                                {processingResults.fraud?.risk_level || 'N/A'}
                              </Badge>
                            </StatNumber>
                          </Stat>
                        </GridItem>
                      </Grid>
                      <Divider />
                      {processingResults.fraud?.alerts && (
                        <VStack spacing={2} align="stretch">
                          <Text fontWeight="bold">Alerts:</Text>
                          {processingResults.fraud.alerts.map((alert, index) => (
                            <Alert
                              key={index}
                              status={alert.severity === 'high' ? 'error' : 'warning'}
                              borderRadius="md"
                            >
                              <AlertIcon />
                              <Box flex="1">
                                <AlertTitle>{alert.title}</AlertTitle>
                                <AlertDescription>{alert.description}</AlertDescription>
                              </Box>
                            </Alert>
                          ))}
                        </VStack>
                      )}
                    </VStack>
                  </TabPanel>
                </TabPanels>
              </Tabs>
            </CardBody>
          </Card>
        )}
      </VStack>
    </Box>
  );
};

export default InvoiceUpload; 