'use client';

import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import '../lib/amplify-config';

export function AuthWrapper({ children }: { children: React.ReactNode }) {
  return (
    <Authenticator>
      {children}
    </Authenticator>
  );
}
