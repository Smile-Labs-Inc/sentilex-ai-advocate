import { PayPalButtons, PayPalScriptProvider } from "@paypal/react-paypal-js";
import { API_CONFIG } from "../../../config";
import { useState } from "preact/hooks";

interface PayPalPaymentProps {
  amount: string; // e.g., "29.99"
  planName: string; // e.g., "Pro Plan"
  onSuccess: (details: any) => void;
  onError?: (error: any) => void;
}

export function PayPalPayment({
  amount,
  planName,
  onSuccess,
  onError,
}: PayPalPaymentProps) {
  const [isPaying, setIsPaying] = useState(false);

  const initialOptions = {
    clientId: API_CONFIG.PAYPAL_CLIENT_ID,
    currency: "USD",
    intent: "capture",
  };

  return (
    <div className="w-full">
      <PayPalScriptProvider options={initialOptions}>
        <PayPalButtons
          disabled={isPaying}
          style={{
            layout: "vertical",
            color: "gold",
            shape: "rect",
            label: "paypal",
          }}
          createOrder={(_data, actions) => {
            setIsPaying(true);
            return actions.order.create({
              intent: "CAPTURE",
              purchase_units: [
                {
                  description: planName,
                  amount: {
                    currency_code: "USD",
                    value: amount,
                  },
                },
              ],
            });
          }}
          onApprove={async (_data, actions) => {
            try {
              const details = await actions.order!.capture();
              
              setIsPaying(false);
              onSuccess(details);
            } catch (error) {
              
              setIsPaying(false);
              onError?.(error);
            }
          }}
          onError={(err) => {
            
            setIsPaying(false);
            onError?.(err);
          }}
          onCancel={() => {
            
            setIsPaying(false);
          }}
        />
      </PayPalScriptProvider>
    </div>
  );
}
