import React from 'react';
import {
  Box,
  Flex,
  HStack,
  IconButton,
  Button,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useColorModeValue,
  useColorMode,
  Text,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { FiMenu, FiMoon, FiSun, FiUser, FiSettings, FiLogOut } from 'react-icons/fi';

const Navbar = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box
      bg={bgColor}
      px={4}
      borderBottom="1px"
      borderColor={borderColor}
      position="sticky"
      top={0}
      zIndex={1000}
    >
      <Flex h={16} alignItems="center" justifyContent="space-between">
        {/* Logo and Brand */}
        <HStack spacing={8} alignItems="center">
          <Text
            as={RouterLink}
            to="/"
            fontSize="xl"
            fontWeight="bold"
            color="blue.500"
            _hover={{ textDecoration: 'none' }}
          >
            NexusAI
          </Text>
          <HStack spacing={4} display={{ base: 'none', md: 'flex' }}>
            <Button
              as={RouterLink}
              to="/"
              variant="ghost"
              size="sm"
            >
              Dashboard
            </Button>
            <Button
              as={RouterLink}
              to="/invoices"
              variant="ghost"
              size="sm"
            >
              Invoices
            </Button>
            <Button
              as={RouterLink}
              to="/upload"
              variant="ghost"
              size="sm"
            >
              Upload
            </Button>
          </HStack>
        </HStack>

        {/* Right side buttons */}
        <HStack spacing={4}>
          <IconButton
            icon={colorMode === 'light' ? <FiMoon /> : <FiSun />}
            onClick={toggleColorMode}
            variant="ghost"
            aria-label="Toggle color mode"
          />
          
          <Menu>
            <MenuButton
              as={Button}
              variant="ghost"
              size="sm"
              leftIcon={<FiUser />}
            >
              Account
            </MenuButton>
            <MenuList>
              <MenuItem icon={<FiUser />}>Profile</MenuItem>
              <MenuItem icon={<FiSettings />}>Settings</MenuItem>
              <MenuItem icon={<FiLogOut />}>Logout</MenuItem>
            </MenuList>
          </Menu>

          <IconButton
            display={{ base: 'flex', md: 'none' }}
            icon={<FiMenu />}
            variant="ghost"
            aria-label="Open menu"
          />
        </HStack>
      </Flex>
    </Box>
  );
};

export default Navbar; 