import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';

export default function Home() {
  const [count, setCount] = React.useState(0);

  console.log('Rendering Home'); // Issue: console.log

  return (
    <View>
      <Text>Count: {count}</Text>
      
      {/* Issue: inline arrow function */}
      <TouchableOpacity onPress={() => setCount(count + 1)}>
        <Text>Increment</Text>
      </TouchableOpacity>
      
      {/* Issue: missing accessibilityLabel */}
      <TouchableOpacity onPress={() => alert('Hello')}>
        <Text>Alert</Text>
      </TouchableOpacity>
    </View>
  );
}
